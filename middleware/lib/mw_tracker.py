import os
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
import logging
import requests
from middleware.version import SDK_VERSION
from middleware.config import config

green_color = "\033[92m"
yellow_color = "\033[93m"
reset_color = "\033[0m"


class MwTracker:
    def __init__(self):

        self.project_name = config.project_name
        self.service_name = config.service_name
        self.access_token = config.access_token or ""

        self._health_check()
        if config.collect_metrics:
            self.collect_metrics()
        if config.collect_traces:
            self.collect_traces()
        if config.collect_logs:
            self.collect_logs()
        if PSUTIL_AVAILABLE:
            if config.collect_profiling and not psutil.WINDOWS:
                self.collect_profiling()
        self._get_instrument_info()

    def collect_metrics(self):
        os.environ["OTEL_PYTHON_METER_PROVIDER"] = "sdk_meter_provider"
        from ._meter import collect_metrics

        collect_metrics()

    def collect_traces(self):
        os.environ["OTEL_PYTHON_TRACER_PROVIDER"] = "sdk_tracer_provider"
        from ._tracer import collect_traces

        collect_traces()

    def collect_profiling(self):
        from ._profiler import collect_profiling

        collect_profiling()

    def collect_logs(self):
        from ._logger import log_handler

        handler = log_handler()
        logging.getLogger().addHandler(handler)
        logging.setLogRecordFactory(self._set_custom_log_attr)

    def record_error(self, error):
        from ._tracer import record_error

        record_error(error)

    def django_instrument(self):
        if config.collect_traces:
            from opentelemetry.instrumentation.django import DjangoInstrumentor
            DjangoInstrumentor().instrument()

    def _set_custom_log_attr(self, *args, **kwargs):
        record = logging.LogRecord(*args, **kwargs)
        update_json = {"service.name": self.service_name, "mw.app.lang": "python"}
        if self.project_name:
            update_json["project.name"] = self.project_name
        record.__dict__.update(update_json)
        return record

    def _get_project_name(self, resource_attributes) -> str:
        project_name = None
        if resource_attributes is not None:
            attributes_list = resource_attributes.split(",")
            for attribute in attributes_list:
                key, value = attribute.split("=")
                if key == "project.name":
                    project_name = value

        return project_name

    def _health_check(self):
        if config.target == "" or ("https" not in config.target) :
            try:
                response = requests.get(
                    f"http://{config.mw_agent_service}:13133/healthcheck", timeout=5
                )
                if response.status_code != 200:
                    print(
                        f"[{yellow_color}WARN{reset_color}]: MW Agent Health Check is failing ...\nThis could be due to incorrect value of MW_AGENT_SERVICE\nIgnore the warning if you are using MW Agent older than 1.7.7 (You can confirm by running `mw-agent version`)"
                    )
            except requests.exceptions.RequestException as e:
                print(f"[{yellow_color}WARN{reset_color}]: MW Agent Health Check is failing ...\nException while MW Agent Health Check:{e}")

    def _get_instrument_info(self):
        if config.disable_info != True:
            print(f"{green_color}")
            print(
                f"Middleware Python Instrumentation Started\nSDK version: {SDK_VERSION}"
            )
            if config.target == "" or ("https" not in config.target):
                print(f"Using Agent Instrumentation")
            else:
                print(f"Using Serverless Instrumentation")
            print(f"OTLP Endpoint:{config.exporter_otlp_endpoint}")
            if config.collect_metrics:
                print(f"Metrics: Enabled")
            if config.collect_traces:
                print(f"Traces: Enabled")
            if config.collect_logs:
                print(f"Logs: Enabled")
            if config.collect_profiling:
                print(f"Profiling: Enabled")
            print(f"{reset_color}")
