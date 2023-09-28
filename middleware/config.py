import os
import sys
import configparser


class Config:
    def __init__(self):
        if len(sys.argv) > 1 and sys.argv[1] == "help":
            return

        config_file = os.environ.get("MIDDLEWARE_CONFIG_FILE")
        if not config_file:
            print("MIDDLEWARE_CONFIG_FILE environment variable is missing. \n")
            sys.exit(1)

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"File not found: {config_file}")

        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file)
        except configparser.Error as e:
            raise RuntimeError(f"Error reading configuration file: {e}")

        self.project_name = self.get_config("middleware.common", "project_name", "Python-APM-Project")
        self.service_name = self.get_config("middleware.common", "service_name", "Python-APM-Service")
        self.access_token = self.get_config("middleware.common", "access_token", "")
        self.collect_traces = self.get_config_boolean("middleware.common", "collect_traces", True)
        self.collect_metrics = self.get_config_boolean("middleware.common", "collect_metrics", False)
        self.collect_logs = self.get_config_boolean("middleware.common", "collect_logs", False)
        self.collect_profiling = self.get_config_boolean("middleware.common", "collect_profiling", False)

        self.exporter_otlp_endpoint = "http://localhost:9319"
        self.resource_attributes = f"project.name={self.project_name},mw.app.lang=python,runtime.metrics.python=true"

    def get_config(self, section, key, default):
        return self.config.get(section, key, fallback=default)

    def get_config_boolean(self, section, key, default):
        return self.config.getboolean(section, key, fallback=default)

config = Config()
