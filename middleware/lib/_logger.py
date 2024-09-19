import logging
import grpc
import sys
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
    ConsoleLogExporter,
)
from middleware.config import config


def log_handler():
    logger_provider = LoggerProvider(shutdown_on_exit=True)
    set_logger_provider(logger_provider)

    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(timeout=5, compression=grpc.Compression.Gzip)
        )
    )

    if config.console_exporter:
        output= sys.stdout    
        if config.debug_log_file:
            output=open("mw-logs.log", "w")
        logger_provider.add_log_record_processor(
            SimpleLogRecordProcessor(ConsoleLogExporter(out=output))
        )


    root_logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    root_logger.addHandler(stream_handler)
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
        'FATAL': logging.FATAL,
    }
    return LoggingHandler(level=log_levels[config.log_level.strip()], logger_provider=logger_provider)
