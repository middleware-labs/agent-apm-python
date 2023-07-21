# import os
from opentelemetry import trace

# mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')


def record_error(error):
    span = trace.get_current_span()
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
