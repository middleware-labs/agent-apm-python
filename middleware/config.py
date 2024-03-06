import os
import sys
import configparser


class Config:
    def __init__(self):
        if len(sys.argv) > 1 and sys.argv[1] == "help":
            return

        config_file = os.environ.get("MIDDLEWARE_CONFIG_FILE", os.path.join(os.getcwd(), 'middleware.ini'))
        if not os.path.exists(config_file):
            exit_with_error(f"File not found: {config_file}")

        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file)
        except configparser.Error as e:
            exit_with_error(f"Error reading configuration file: {e}")

        pid = os.getpid()
        self.project_name = self.get_config("middleware.common", "project_name", None)
        self.service_name = self.get_config("middleware.common", "service_name", f"Service-{pid}")
        self.access_token = self.get_config("middleware.common", "access_token", "")
        self.collect_traces = self.get_config_boolean("middleware.common", "collect_traces", True)
        self.collect_metrics = self.get_config_boolean("middleware.common", "collect_metrics", False)
        self.collect_logs = self.get_config_boolean("middleware.common", "collect_logs", False)
        self.collect_profiling = self.get_config_boolean("middleware.common", "collect_profiling", False)
        self.otel_propagators = self.get_config("middleware.common", "otel_propagators", "b3")

        project_name_attr = f"project.name={self.project_name}," if self.project_name else ""
        source_service_url = self.get_config("middleware.common", "mw_agent_service", "localhost")

        mw_agent_service = os.environ.get("MW_AGENT_SERVICE", None)
        if mw_agent_service is not None and mw_agent_service != "":
            source_service_url = mw_agent_service

        self.exporter_otlp_endpoint = f"http://{source_service_url}:9319"
        self.resource_attributes = f"{project_name_attr}mw.app.lang=python,runtime.metrics.python=true"

    def get_config(self, section, key, default):
        return self.config.get(section, key, fallback=default)

    def get_config_boolean(self, section, key, default):
        return self.config.getboolean(section, key, fallback=default)


def exit_with_error(message):
    print(message)
    sys.exit(1)


config = Config()
