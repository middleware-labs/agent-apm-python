import os
import logging
from ._meter import collect_metrics
from ._tracer import record_error
from ._logger import log_handler
from ._profiler import collect_profiling

mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')


class MwTracker:
    def __init__(self, access_token=None):
        pid = os.getpid()
        os.environ["OTEL_TRACES_EXPORTER"] = "otlp"
        os.environ["OTEL_METRICS_EXPORTER"] = "otlp"
        os.environ["OTEL_LOGS_EXPORTER"] = "otlp"

        # Way 1:
        # project_name = project_name or f"Project-{pid}"
        # service_name = service_name or f"Service-{pid}"
        # access_token = access_token or ""

        # os.environ["OTEL_SERVICE_NAME"] = service_name
        # os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"project.name={project_name},mw.app.lang=python,runtime.metrics.python=true"

        # Way 2:
        resource_attributes = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
        _service_name = os.environ.get("OTEL_SERVICE_NAME")
        _project_name = self._get_project_name(resource_attributes)

        project_name = _project_name or f"Project-{pid}"
        service_name = _service_name or f"Service-{pid}"
        access_token = access_token or ""

        # Set values in self
        self.project_name = project_name
        self.service_name = service_name
        self.access_token = access_token

    # For Metrics
    def collect_metrics(self):
        collect_metrics()

    # For Profiling
    def collect_profiling(self) -> None:
        collect_profiling(self.service_name, self.access_token)

    # For Logging
    def collect_logs(self):
        handler = log_handler(self.project_name, self.service_name)
        logging.getLogger().addHandler(handler)
        logging.setLogRecordFactory(self._set_custom_log_attr)

    # For Tracing
    def record_error(self, error):
        record_error(error)

    # For Utils
    def _set_custom_log_attr(self, *args, **kwargs):
        record = logging.LogRecord(*args, **kwargs)
        record.__dict__.update({
            "project.name": self.project_name,
            "service.name": self.service_name,
            "mw.app.lang": "python"
        })
        return record

    def _get_project_name(self, resource_attributes) -> str:
        project_name = None
        if resource_attributes is not None:
            attributes_list = resource_attributes.split(',')
            for attribute in attributes_list:
                key, value = attribute.split('=')
                if key == 'project.name':
                    project_name = value

        return project_name
