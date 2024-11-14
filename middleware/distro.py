import logging
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
from opentelemetry.trace import Tracer, get_current_span, get_tracer

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


def record_exception(exc: Exception, span_name: Optional[str] = None) -> None:
    """
    Reports an exception as a span event creating a dummy span if necessary.

    Args:
        exc (Exception): Pass Exception to record as in a current span.
        span_name (String,Optional): Span Name to use if no current span found,
                                     defaults to Exception Name.

    Example
    --------
    >>> from middleware import record_exception
    >>> try:
    >>>     print("Divide by zero:",1/0)
    >>> except Exception as e:
    >>>     record_exception(e)

    """

    span = get_current_span()
    if span.is_recording():
        span.record_exception(exc)
        return

    tracer: Tracer = get_tracer("mw-tracer")
    if span_name is None:
        span_name = type(exc).__name__

    span = tracer.start_span(span_name)
    span.record_exception(exc)
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
    span.end()


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
