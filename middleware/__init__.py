from middleware.distro import mw_tracker, record_exception
from typing import Collection
import sys
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

class ExceptionInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        """Return dependencies if this instrumentor requires any."""
        return []
    
    def _instrument(self, **kwargs):
        """Automatically sets sys.excepthook when the instrumentor is loaded."""
        sys.excepthook = record_exception

    def _uninstrument(self, **kwargs):
        """Restores default sys.excepthook if needed."""
        sys.excepthook = sys.__excepthook__

# Load the instrumentor
ExceptionInstrumentor().instrument()

