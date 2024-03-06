import os
import psutil
import logging
from middleware.config import config

mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')


class MwTracker:
    def __init__(self):

        # resource_attributes = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
        # _service_name = os.environ.get("OTEL_SERVICE_NAME")
        # _project_name = self._get_project_name(resource_attributes)

        self.project_name = config.project_name
        self.service_name = config.service_name
        self.access_token = config.access_token or ""

        if config.collect_metrics: self.collect_metrics()
        if config.collect_traces: self.collect_traces()
        if config.collect_logs: self.collect_logs()
        if config.collect_profiling and not psutil.WINDOWS: self.collect_profiling()

    def collect_metrics(self):
        from ._meter import collect_metrics
        collect_metrics()

    def collect_traces(self):
        os.environ['OTEL_PYTHON_TRACER_PROVIDER'] = 'sdk_tracer_provider'
        from ._tracer import collect_traces
        collect_traces()

    def collect_profiling(self):
        from ._profiler import collect_profiling
        collect_profiling(self.service_name, self.access_token)

    def collect_logs(self):
        from ._logger import log_handler
        handler = log_handler(self.project_name, self.service_name)
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
        if self.project_name: update_json["project.name"] = self.project_name
        record.__dict__.update(update_json)
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
