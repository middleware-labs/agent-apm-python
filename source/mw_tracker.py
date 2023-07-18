import os
import logging
from _meter import collect_metrics
from _tracer import track, record_error
from _logger import log_handler

class MwTracker:
    def __init__(self, project_name=None, service_name=None, access_token=None):

        pid = os.getpid()
        if project_name is None:
            project_name = "Project-" + str(pid)
        if service_name is None:
            service_name = "Service-" + str(pid)
        if access_token is None:
            access_token = ""

        self.project_name = project_name
        self.service_name = service_name
        self.access_token = access_token

        handler = log_handler(self.project_name, self.service_name)
        logging.getLogger().addHandler(handler)
        logging.setLogRecordFactory(self._set_custom_log_attr)

    # For Metrics
    def collect_metrics(self):
        collect_metrics(self.project_name, self.service_name)

    # For Tracing
    def track(self) -> None:
        track(self.project_name, self.service_name, self.access_token)

    def record_error(self, error):
        record_error(error)

    # def set_attribute(self, key, value):
    #     set_attribute(key, value)

    # For Logging
    def log_handler(self):
        return log_handler(self.project_name, self.service_name)

    def error(self, message) -> None:
        # emit_log(self.project_name, self.service_name, 'error', message)
        logging.error(message)

    def info(self, message) -> None:
        # emit_log(self.project_name, self.service_name, 'info', message)
        logging.info(message)

    def warning(self, message) -> None:
        # emit_log(self.project_name, self.service_name, 'warn', message)
        logging.warning(message)

    def debug(self, message) -> None:
        # emit_log(self.project_name, self.service_name, 'debug', message)
        logging.debug(message)

    def _set_custom_log_attr(self, *args, **kwargs):
        record = logging.LogRecord(*args, **kwargs)
        record.__dict__.update({
            "project.name": self.project_name,
            "service.name": self.service_name,
            "mw.app.lang": "python"
        })
        return record