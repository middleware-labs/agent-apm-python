from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')


def collect_traces():
    provider = trace.get_tracer_provider()
    if not provider:
        trace.set_tracer_provider(TracerProvider())
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))


def record_error(error):
    span = trace.get_current_span()
    if span:
        span.record_exception(error)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))


# def set_attribute(name, value):
#     if type(name) is not str:
#         print("name must be a string")
#         return
#     if type(value) is not str:
#         print("value must be a string")
#         return
#     span = trace.get_current_span()
#     span.set_attribute(name, value)
