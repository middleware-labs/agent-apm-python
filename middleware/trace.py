# import grpc
import sys
import logging
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor, ReadableSpan
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.processor.baggage import ALLOW_ALL_BAGGAGE_KEYS, BaggageSpanProcessor
from middleware.options import MWOptions
from opentelemetry.trace import set_tracer_provider, Span
from middleware.sampler import configure_sampler

_logger = logging.getLogger(__name__)

class ExceptionFilteringSpanProcessor(SpanProcessor):
    def on_start(self, span: ReadableSpan, parent_context):
        pass

    def on_end(self, span: ReadableSpan):
        # Check if there is any "exception" event with "exception.stack_details"
        has_stack_details = any(
            event.name == "exception" and "exception.stack_details" in event.attributes
            for event in span.events
        )

        if has_stack_details:
            # Keep only the unique "exception" events based on "exception.stack_trace"
            seen_stack_traces = set()
            filtered_events = []
            for event in span.events:
                if event.name == "exception" and "exception.stack_details" in event.attributes:
                    stack_trace = event.attributes.get("exception.stack_trace")
                    seen_stack_traces.add(stack_trace)
                    filtered_events.append(event)
                elif event.name == "exception":
                    stack_trace = event.attributes.get("exception.stack_trace")
                    if stack_trace not in seen_stack_traces:
                        filtered_events.append(event)
                elif event.name != "exception":
                    filtered_events.append(event)
            span._events = filtered_events

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=None):
        pass

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
        endpoint=options.target + "/v1/traces",
        # compression=grpc.Compression.Gzip,
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
    trace_provider.add_span_processor(ExceptionFilteringSpanProcessor())
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