import logging
import inspect
import traceback
from typing import Optional, Type
import sys
from logging import getLogger
from typing import Optional
from opentelemetry.instrumentation.distro import BaseDistro
from middleware.metrics import create_meter_provider
from middleware.options import MWOptions, parse_bool
from middleware.resource import create_resource
from middleware.trace import create_tracer_provider
from middleware.log import create_logger_handler
from middleware.profiler import collect_profiling
from opentelemetry import trace
from opentelemetry.trace import Tracer, get_current_span, get_tracer, Span, get_tracer, Status, StatusCode
import os
import json

_logger = getLogger(__name__)

mw_tracker_called = False
distro_called = False
MW_TRACKER = "MW_TRACKER"
DEFAULT_TRACKER = False
isTracker = parse_bool(
    MW_TRACKER, DEFAULT_TRACKER, "Invalid MW_TRACKER: expected boolean"
)


def mw_tracker(
    options: Optional[MWOptions] = None,
):
    """
    Configures the OpenTelemetry SDK to send telemetry to middleware.

    Args:
        options (MWOptions, optional): the MWOptions used to
        configure the the SDK. These options can be set either as parameters
        to this function or through environment variables

    Example
    --------
    >>> from middleware import mw_tracker, MWOptions, record_exception, DETECT_AWS_EC2
    >>> mw_tracker(
    >>>     MWOptions(
    >>>         access_token="whkvkobudfitutobptgonaezuxpjjypnejbb",
    >>>         target="https://myapp.middleware.io:443",
    >>>         console_exporter=True,
    >>>         debug_log_file=True,
    >>>         service_name="MyPythonServer",
    >>>         otel_propagators = "b3,tracecontext",
    >>>         custom_resource_attributes="call_id=12345678, request_id=987654321",
    >>>         detectors=[DETECT_AWS_EC2]
    >>>     )
    >>> )

    """
    global mw_tracker_called, isTracker

    if not distro_called:
        return
    if not isTracker and mw_tracker_called:
        _logger.warning(
            "Skipping mw_tracker config: `export MW_TRACKER=True` to use config settings"
        )
        return
    if isTracker and mw_tracker_called:
        _logger.warning("Skipping mw_tracker config: overriding of config not allowed")
        return

    if options is None:
        options = MWOptions()

    _logger.debug(vars(options))
    resource = create_resource(options)
    if options.collect_traces:
        create_tracer_provider(options, resource)
    if options.collect_metrics:
        create_meter_provider(options, resource)
    if options.collect_logs:
        handler = create_logger_handler(options, resource)
        logging.getLogger().addHandler(handler)
    if options.collect_profiling:
        collect_profiling(options)    

    mw_tracker_called = True

def extract_function_code(tb_frame, lineno):
    """Extracts the full function body where the exception occurred."""
    try:
        source_lines, start_line = inspect.getsourcelines(tb_frame)
        end_line = start_line + len(source_lines) - 1
        
        if len(source_lines) > 20:
            # Get 10 lines above and 10 below the exception line
            start_idx = max(0, lineno - start_line - 10)
            end_idx = min(len(source_lines), lineno - start_line + 10)
            source_lines = source_lines[start_idx:end_idx]
        
        function_code = "".join(source_lines)  # Convert to a string
        
        return {
            "function_code": function_code,
            "function_start_line": start_line if len(source_lines) <= 20 else None,
            "function_end_line": end_line if len(source_lines) <= 20 else None,
        }    
        
    except Exception as e:
        return {
            "function_code": f"Error extracting function code: {e}",
            "function_start_line": None,
            "function_end_line": None
        }

# Replacement of span.record_exception to include function source code
def custom_record_exception(span: Span, exc: Exception):
    """Custom exception recording that captures function source code."""
    exc_type, exc_value, exc_tb = exc.__class__, str(exc), exc.__traceback__

    if exc_tb is None:
        span.set_attribute("exception.warning", "No traceback available")
        span.record_exception(exc)
        return

    tb_details = traceback.extract_tb(exc_tb)
    
    if not tb_details:
        span.set_attribute("exception.warning", "Traceback is empty")
        span.record_exception(exc)
        return

    stack_info = []
    
    for (frame, _), (filename, lineno, func_name, _) in zip(traceback.walk_tb(exc_tb), tb_details):
        function_details = extract_function_code(frame, lineno) if frame else "Function source not found."
  
        stack_entry = {
            "exception.file": filename,
            "exception.line": lineno,
            "exception.function_name": func_name,
            "exception.function_body": function_details["function_code"],
            "exception.start_line": function_details["function_start_line"],
            "exception.end_line": function_details["function_end_line"],
        }

        # Check if the file is from site-packages
        if "site-packages" in filename:
            stack_entry["exception.is_file_internal"] = "true"
        else:
            stack_entry["exception.is_file_internal"] = "false"

        stack_info.insert(0, stack_entry)  # Prepend instead of append

    # Determine if the exception is escaping
    current_exc = sys.exc_info()[1]  # Get the currently active exception
    exception_escaped = current_exc is exc  # True if it's still propagating

    mw_vcs_repository_url = os.getenv("MW_VCS_REPOSITORY_URL")
    mw_vcs_commit_sha = os.getenv("MW_VCS_COMMIT_SHA")
  
    # Serialize stack info as JSON string since OpenTelemetry only supports string values
    stack_info_str = json.dumps(stack_info, indent=2)
    
    # Add extra details in the existing "exception" event
    span.add_event(
        "exception",  
        {
            "exception.type": str(exc_type.__name__),
            "exception.message": exc_value,
            "exception.stacktrace": traceback.format_exc(),
            "exception.escaped": exception_escaped,
            "exception.vcs.commit_sha": mw_vcs_commit_sha or "",
            "exception.vcs.repository_url": mw_vcs_repository_url or "",
            "exception.stack_details": stack_info_str,  # Attach full stacktrace details
        }
    )

def record_exception(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback) -> None:
    """
    Reports an exception as a span event, creating a dummy span if necessary.

    Args:
        exc_type (Type[BaseException]): The type of the exception.
        exc_value (BaseException): The exception instance.
        exc_traceback: The traceback object.

    Example
    --------
    >>> import sys
    >>> try:
    >>>     print("Divide by zero:", 1 / 0)
    >>> except Exception as e:
    >>>     sys.excepthook(*sys.exc_info())

    """
    # Retrieve the current span if available
    span = get_current_span()
    if span and span.is_recording():
        custom_record_exception(span, exc_value)
        return

    # Create a new span if none is found
    tracer: Tracer = get_tracer("mw-tracer")
    span_name = exc_type.__name__ if exc_type else "UnknownException"

    with tracer.start_span(span_name) as span:
        custom_record_exception(span, exc_value)
        span.set_status(Status(StatusCode.ERROR, str(exc_value)))


# pylint: disable=too-few-public-methods
class MiddlewareDistro(BaseDistro):
    """
    An extension of the base python OpenTelemetry distro, which provides
    a mechanism to automatically configure some of the more common options
    for users. This class is auto-detected by the `opentelemetry-instrument`
    command.

    This class doesn't need to be touched directly when using the distro. If
    you'd like to explicitly set configuration in code, use the
    mw_tracker() function above with `export MW_TRACKER=True`.

    [tool.poetry.plugins."opentelemetry_distro"]
    distro = "middleware.opentelemetry.distro:MiddlewareDistro"
    """

    def _configure(self, **kwargs):
        global isTracker, distro_called
        distro_called = True
        if not isTracker:
            mw_tracker()
