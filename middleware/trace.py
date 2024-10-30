import grpc
import sys
import logging
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.processor.baggage import ALLOW_ALL_BAGGAGE_KEYS, BaggageSpanProcessor
from middleware.options import MWOptions
from opentelemetry.trace import set_tracer_provider
from middleware.sampler import configure_sampler

_logger = logging.getLogger(__name__)


def create_tracer_provider(options: MWOptions, resource: Resource) -> TracerProvider:
    """
    Configures and returns a new TracerProvider to send traces telemetry.

    Args:
        options (MWOptions): the middleware options to configure with
        resource (Resource): the resource to use with the new tracer provider

    Returns:
        TracerProvider: the new tracer provider
    """
    exporter = OTLPSpanExporter(
        endpoint=options.target,
        compression=grpc.Compression.Gzip,
    )
    trace_provider = TracerProvider(
        resource=resource, shutdown_on_exit=True, sampler=configure_sampler(options)
    )
    trace_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            exporter,
        )
    )
    if options.console_exporter:
        output = sys.stdout
        if options.debug_log_file:
            log_file = "mw-traces"
            try:
                output = open(log_file, "w")
            except Exception:
                _logger.error(f"Cannot open the log file for writing: {log_file}")
                output = sys.stdout
        trace_provider.add_span_processor(
            SimpleSpanProcessor(
                ConsoleSpanExporter(
                    out=output,
                )
            )
        )
    set_tracer_provider(tracer_provider=trace_provider)
    return trace_provider
