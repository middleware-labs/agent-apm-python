import os
import sys
import shutil
# from importlib.resources import path
import pkg_resources
import configparser
from middleware.version import SDK_VERSION, PYTHON_VERSION

CONFIG_FILE_PATH = os.getenv('MIDDLEWARE_CONFIG_FILE', os.path.join(os.getcwd(), "middleware.ini"))
DEFAULT_CONFIG_FILE_PATH = pkg_resources.resource_filename('middleware', 'middleware.ini')
# DEFAULT_CONFIG_FILE_PATH = path('middleware','middleware.ini')

class Config:
    def get_config(self, section, key, default):
        # Allowing OTEL level overrides at top priority
        if key in self.otel_config_binding:
            otel_env_value = os.environ.get(self.otel_config_binding[key], None)
            if otel_env_value is not None and otel_env_value != "":
                return otel_env_value

        # Allowing MW level ENV overrides
        if key in self.config_binding:
            env_value = os.environ.get(self.config_binding[key], None)
            if env_value is not None and env_value != "":
                return env_value

        return self.config.get(section, key, fallback=default)

    def str_to_bool(self, value, default):
        if isinstance(value, str):
            value = value.strip().lower()
            if value in {"true", "1", "yes", "y"}:
                return True
            elif value in {"false", "0", "no", "n"}:
                return False
        return default  # Default value if the string cannot be converted

    def get_config_boolean(self, section, key, default):
        # Allowing OTEL level overrides at top priority
        if key in self.otel_config_binding:
            otel_env_value = os.environ.get(self.otel_config_binding[key], None)
            if otel_env_value is not None and otel_env_value != "":
                return self.str_to_bool(otel_env_value, default)

        # Allowing MW level ENV overrides
        if key in self.config_binding:
            env_value = os.environ.get(self.config_binding[key], None)
            if env_value is not None and env_value != "":
                return self.str_to_bool(env_value, default)

        return self.config.getboolean(section, key, fallback=default)

    def __init__(self):
        if len(sys.argv) > 1 and sys.argv[1] == "help":
            return

        self.config_binding = {
            "project_name": "MW_PROJECT_NAME",
            "service_name": "MW_SERVICE_NAME",
            "access_token": "MW_API_KEY",
            "collect_traces": "MW_APM_COLLECT_TRACES",
            "collect_metrics": "MW_APM_COLLECT_METRICS",
            "collect_logs": "MW_APM_COLLECT_LOGS",
            "collect_profiling": "MW_APM_COLLECT_PROFILING",
            "otel_propagators": "MW_PROPAGATORS",
            "mw_agent_service": "MW_AGENT_SERVICE",
            "target": "MW_TARGET",
            "custom_resource_attributes": "MW_CUSTOM_RESOURCE_ATTRIBUTES",
            "log_level": "MW_LOG_LEVEL",
            "console_exporter": "MW_CONSOLE_EXPORTER",
            "disable_info":"MW_DISABLE_INFO",
            "debug_log_file":"MW_DEBUG_LOG_FILE"
        }

        self.otel_config_binding = {
            "service_name": "OTEL_SERVICE_NAME",
            "otel_propagators": "OTEL_PROPAGATORS",
            "target": "OTEL_EXPORTER_OTLP_ENDPOINT",
            "log_level": "OTEL_LOG_LEVEL",
        }

        if not os.path.exists(CONFIG_FILE_PATH):
            print(f"Generated default config file: {CONFIG_FILE_PATH}")
            shutil.copy(DEFAULT_CONFIG_FILE_PATH, CONFIG_FILE_PATH)
        
        config_file = os.environ.get("MIDDLEWARE_CONFIG_FILE", os.path.join(os.getcwd(), 'middleware.ini'))
        self.config = configparser.ConfigParser(empty_lines_in_values=False)
        try:
            self.config.read(config_file)
        except configparser.Error as e:
            exit_with_error(f"Error reading configuration file: {e}")

        pid = os.getpid()
        self.project_name = self.get_config("middleware.common", "project_name", "")
        self.service_name = self.get_config(
            "middleware.common", "service_name", f"Service-{pid}"
        )
        self.mw_agent_service = self.get_config(
            "middleware.common", "mw_agent_service", "localhost"
        )
        self.target = self.get_config("middleware.common", "target", "")
        self.access_token = self.get_config("middleware.common", "access_token", "")
        self.collect_traces = self.get_config_boolean(
            "middleware.common", "collect_traces", True
        )
        self.collect_metrics = self.get_config_boolean(
            "middleware.common", "collect_metrics", False
        )
        self.collect_logs = self.get_config_boolean(
            "middleware.common", "collect_logs", True
        )
        self.collect_profiling = self.get_config_boolean(
            "middleware.common", "collect_profiling", False
        )
        self.otel_propagators = self.get_config(
            "middleware.common", "otel_propagators", "b3"
        )
        self.custom_resource_attributes = self.get_config(
            "middleware.common", "custom_resource_attributes", ""
        )
        self.log_level = self.get_config("middleware.common", "log_level", "INFO")
        self.console_exporter = self.get_config_boolean(
            "middleware.common", "console_exporter", False
        )
        self.debug_log_file = self.get_config_boolean(
            "middleware.common", "debug_log_file", False
        )
        self.disable_info = self.get_config_boolean(
            "middleware.common", "disable_info", False
        )

        self.resource_attributes = f"mw.app.lang=python,runtime.metrics.python=true,mw.sdk.version={SDK_VERSION},python.version={PYTHON_VERSION}"

        if self.mw_agent_service != "":
            self.exporter_otlp_endpoint = f"http://{self.mw_agent_service}:9319"
            if self.target is not None and self.target != "":
                # Add `mw_serverless` resource attribute if target is not "localhost" or agent based
                # target will have more priority over mw_agent_service
                self.resource_attributes = f"{self.resource_attributes},mw_serverless=true"
                self.exporter_otlp_endpoint = self.target

        # Passing Project name as a resource attribute
        if self.project_name is not None and self.project_name != "":
            self.resource_attributes = (
                f"{self.resource_attributes},project.name={self.project_name}"
            )

        # Passing Middleware API Key as a resource attribute, to validate ingestion requests in serverless setup
        if self.access_token is not None and self.access_token != "":
            self.resource_attributes = (
                f"{self.resource_attributes},mw.account_key={self.access_token}"
            )

        # Appending Custom Resource Attributes, if any
        if (
            self.custom_resource_attributes is not None
            and self.custom_resource_attributes != ""
        ):
            self.resource_attributes = (
                f"{self.resource_attributes},{self.custom_resource_attributes}"
            )


def exit_with_error(message):
    print(message)
    sys.exit(1)


config = Config()
