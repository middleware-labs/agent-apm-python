import grpc
import sys
import logging
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
    ConsoleLogExporter,
)
from opentelemetry._logs import set_logger_provider
from logging import LogRecord
from middleware.options import MWOptions, log_levels

_logger = logging.getLogger(__name__)


def create_logger_handler(options: MWOptions, resource: Resource) -> LoggingHandler:
    """
    Configures and returns a new LoggerProvider to send logs telemetry.

    Args:
        options (MWOptions): the middleware options to configure with
        resource (Resource): the resource to use with the new logger provider

    Returns:
        LoggerProvider: the new logger provider
    """
    exporter = OTLPLogExporter(
        endpoint=options.target,
        compression=grpc.Compression.Gzip,
    )
    logger_provider = LoggerProvider(resource=resource, shutdown_on_exit=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    if options.console_exporter:
        if options.console_exporter:
            output = sys.stdout
            if options.debug_log_file:
                log_file = "mw-logs"
                try:
                    output = open(log_file, "w")
                except Exception:
                    _logger.error(f"Cannot open the log file for writing: {log_file}")
                    output = sys.stdout
        logger_provider.add_log_record_processor(
            SimpleLogRecordProcessor(
                ConsoleLogExporter(
                    out=output,
                )
            )
        )

    handler = MWLoggingHandler(
        level=log_levels[options.log_level], logger_provider=logger_provider
    )
    set_logger_provider(logger_provider)

    return handler

class MWLoggingHandler(LoggingHandler):
    @staticmethod
    def _get_attributes(record: LogRecord):
        attributes = LoggingHandler._get_attributes(record)
        if "request" in attributes:
            attributes["request"] = f'{attributes["request"].method} {attributes["request"].path}'
        return attributes