from middleware.distro import mw_tracker, custom_record_exception_wrapper
from typing import Collection
import sys
import threading
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import Span
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
Span.record_exception = custom_record_exception_wrapper