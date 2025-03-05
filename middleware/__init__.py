from middleware.distro import mw_tracker, record_exception
from typing import Collection
import sys
import threading
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry import trace
from typing import Optional
from middleware.options import (
    MWOptions,
    DETECT_AWS_BEANSTALK,
    DETECT_AWS_EC2,
    DETECT_AWS_ECS,
    DETECT_AWS_EKS,
    DETECT_AWS_LAMBDA,
    DETECT_AZURE_APP_SERVICE,
    DETECT_AZURE_FUNCTIONS,
    DETECT_AZURE_VM,
    DETECT_GCP,
    DETECT_ENVVARS,
)

__all__ = [
    "mw_tracker",
    "record_exception",
    "MWOptions",
    "DETECT_AWS_BEANSTALK",
    "DETECT_AWS_EC2",
    "DETECT_AWS_ECS",
    "DETECT_AWS_EKS",
    "DETECT_AWS_LAMBDA",
    "DETECT_AZURE_APP_SERVICE",
    "DETECT_AZURE_FUNCTIONS",
    "DETECT_AZURE_VM",
    "DETECT_GCP",
    "DETECT_ENVVARS",
]

tracer = trace.get_tracer(__name__)

# Hook for threading exceptions (Python 3.8+)
def thread_excepthook(args):
    record_exception(args.exc_type, args.exc_value, args.exc_traceback)

class ExceptionInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        """Return dependencies if this instrumentor requires any."""
        return []
    
    def _instrument(self, **kwargs):
        """Automatically sets sys.excepthook when the instrumentor is loaded."""
        sys.excepthook = record_exception
        threading.excepthook = thread_excepthook

    def _uninstrument(self, **kwargs):
        """Restores default sys.excepthook if needed."""
        sys.excepthook = sys.__excepthook__

# Load the instrumentor
ExceptionInstrumentor().instrument()

# Automatic exception handling for flask
from flask import Flask, request
from flask.signals import got_request_exception, appcontext_pushed
import traceback

def _capture_exception(sender, exception, **extra):
    exc_type, exc_value, exc_traceback = sys.exc_info()  # Get exception details
    if exc_type and exc_value and exc_traceback:
        record_exception(exc_type, exc_value, exc_traceback)
    else:
        print("Unable to capture exception details.")

def try_register_flask_handler(app: Flask):
    """Registers the exception handler using Flask signals."""
    got_request_exception.connect(_capture_exception, app)
    print("✅ Flask error handler registered via signal.")

def _auto_register(sender, **extra):
    """Automatically registers the handler when a Flask app context is pushed."""
    try_register_flask_handler(sender)

# Connect to Flask's appcontext_pushed to register automatically
appcontext_pushed.connect(_auto_register)


