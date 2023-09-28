import os
import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')


def log_handler(project_name, service_name):
    resource_json = {
        "service.name": service_name,
    }

    if project_name is not None:
        resource_json["project.name"] = project_name

    logger_provider = LoggerProvider(
        resource=Resource.create(resource_json),
    )
    set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(
        OTLPLogExporter(insecure=True, endpoint=mw_agent_target+":9319")
    ))
    return LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
