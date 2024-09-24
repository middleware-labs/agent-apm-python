import grpc
import sys
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from middleware.config import config


def collect_traces():
    provider = trace.get_tracer_provider()
    if not provider:
        trace.set_tracer_provider(TracerProvider())

    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(timeout=5, compression=grpc.Compression.Gzip)
        )
    )
    if config.console_exporter:
        output= sys.stdout    
        if config.debug_log_file:
            output=open("mw-traces.log", "w")
        provider.add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter(out=output))
        )


def record_error(error):
    span = trace.get_current_span()
    if span:
        span.record_exception(error)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))
