"""
Exporter configuration that adapts based on the package variant.
Automatically selects HTTP or gRPC exporters based on installed package.

- middleware-io: gRPC exporters (standard)
- middleware-io-k8s: HTTP exporters (for Kubernetes)
"""

import logging
from middleware.version import __package_name__, __version__

_logger = logging.getLogger(__name__)

# PACKAGE VARIANT DETECTION

IS_K8S_VARIANT = "k8s" in __package_name__.lower()

_logger.info(f"Detected package: {__package_name__}")

# IMPORT APPROPRIATE EXPORTERS

if IS_K8S_VARIANT:
    # K8s variant - MUST use HTTP exporters
    try:
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
            OTLPMetricExporter as MetricExporter,
        )
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter as TraceExporter,
        )
        from opentelemetry.exporter.otlp.proto.http._log_exporter import (
            OTLPLogExporter as LogExporter,
        )

        _logger.info("✓ Using HTTP exporters for K8s variant")
    except ImportError as e:
        _logger.error(f"Failed to import HTTP exporters for K8s variant: {e}")
        raise ImportError(
            f"middleware-io-k8s package requires HTTP exporter dependencies. "
            f"Please ensure 'opentelemetry-exporter-otlp-proto-http' is installed. "
            f"Original error: {e}"
        ) from e
else:
    # Standard variant - MUST use gRPC exporters
    try:
        import grpc
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter as MetricExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter as TraceExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
            OTLPLogExporter as LogExporter,
        )

        _logger.info("✓ Using gRPC exporters for standard variant")
    except ImportError as e:
        _logger.error(f"Failed to import gRPC exporters for standard variant: {e}")
        raise ImportError(
            f"middleware-io package requires gRPC exporter dependencies. "
            f"Please ensure 'opentelemetry-exporter-otlp-proto-grpc' is installed. "
            f"Original error: {e}"
        ) from e


def create_metric_exporter(endpoint: str):
    """
    Create OTLP metric exporter of appropriate type.

    Args:
        endpoint (str): The OTLP endpoint URL

    Returns:
        OTLPMetricExporter: HTTP or gRPC based on package variant
    """
    if IS_K8S_VARIANT:
        # K8s: HTTP exporter
        return MetricExporter(endpoint=endpoint + "/v1/metrics")
    else:
        # Standard: gRPC exporter with compression
        return MetricExporter(endpoint=endpoint, compression=grpc.Compression.Gzip)


def create_trace_exporter(endpoint: str):
    """
    Create OTLP trace exporter of appropriate type.

    Args:
        endpoint (str): The OTLP endpoint URL

    Returns:
        OTLPSpanExporter: HTTP or gRPC based on package variant
    """
    if IS_K8S_VARIANT:
        # K8s: HTTP exporter
        return TraceExporter(endpoint=endpoint + "/v1/traces")
    else:
        # Standard: gRPC exporter with compression
        return TraceExporter(endpoint=endpoint, compression=grpc.Compression.Gzip)


def create_log_exporter(endpoint: str):
    """
    Create OTLP log exporter of appropriate type.

    Args:
        endpoint (str): The OTLP endpoint URL

    Returns:
        OTLPLogExporter: HTTP or gRPC based on package variant
    """
    if IS_K8S_VARIANT:
        # K8s: HTTP exporter
        return LogExporter(endpoint=endpoint + "/v1/logs")
    else:
        # Standard: gRPC exporter with compression
        return LogExporter(endpoint=endpoint, compression=grpc.Compression.Gzip)
