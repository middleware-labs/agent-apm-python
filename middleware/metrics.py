import psutil
import os
import threading
import gc
import grpc
import sys
import logging
from sys import getswitchinterval
from typing import NamedTuple
from opentelemetry.metrics import CallbackOptions, Observation, set_meter_provider
import grpc
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider, Meter
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from middleware.options import MWOptions

_logger = logging.getLogger(__name__)


def create_meter_provider(options: MWOptions, resource: Resource):
    """
    Configures and returns a new MeterProvider to send metrics telemetry.

    Args:
        options (MWOptions): the middleware options to configure with
        resource (Resource): the resource to use with the new meter provider

    Returns:
        MeterProvider: the new meter provider
    """

    exporter = OTLPMetricExporter(
        endpoint=options.target,
        compression=grpc.Compression.Gzip,
    )
    readers = [PeriodicExportingMetricReader(exporter)]
    if options.console_exporter:
        output = sys.stdout
        if options.debug_log_file:
            log_file = "mw-metrics"
            try:
                output = open(log_file, "w")
            except Exception:
                _logger.error(f"Cannot open the log file for writing: {log_file}")
                output = sys.stdout
        readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter(
                    out=output,
                ),
            )
        )

    provider = MeterProvider(metric_readers=readers, resource=resource)

    meter = provider.get_meter("sdk_meter_provider")
    _generate_metrics(meter)

    set_meter_provider(meter_provider=provider)

    return provider


class DiskUsageData(NamedTuple):
    total: int
    used: int
    free: int
    percent: float


def _generate_metrics(meter: Meter):
    meter.create_observable_gauge(
        "process.cpu_usage.percentage",
        unit="Percent",
        callbacks=[_cpu_usage_cb],
        description="The will show the cpu usage of the process",
    )
    meter.create_observable_gauge(
        "process.memory_usage.percentage",
        unit="Percent",
        callbacks=[_ram_usage_cb],
        description="The will show the memory usage of the process",
    )
    meter.create_observable_counter(
        "process.cpu.time",
        callbacks=[_cpu_time_callback],
        unit="s",
        description="This will show the cpu time of the process",
    )
    meter.create_observable_gauge(
        "process.memory.bytes",
        unit="Bytes",
        callbacks=[
            _memory_rss_cb,
            _memory_vms_cb,
            _memory_shared_cb,
            _memory_text_cb,
            _memory_data_cb,
        ],
        description="The will show the memory rss, vms, shared, text and data of the process",
    )
    meter.create_observable_gauge(
        "process.num_threads.count",
        unit="Count",
        callbacks=[_num_threads_cb],
        description="The will show the number of threads of the process",
    )
    meter.create_observable_gauge(
        "process.num_fds.count",
        unit="Count",
        callbacks=[_num_fds_cb],
        description="The will show the number of fds of the process",
    )
    meter.create_observable_gauge(
        "process.ctx_switches.count",
        unit="Count",
        callbacks=[_num_vctx_switches_cb, _num_ivctx_switches_cb],
        description="The will show the number of ctx switches of the process",
    )
    meter.create_observable_gauge(
        "process.num_connections.count",
        unit="Count",
        callbacks=[_num_connections_cb],
        description="The will show the number of connections of the process",
    )
    meter.create_observable_gauge(
        "process.io_counters.bytes",
        unit="Bytes",
        callbacks=[_io_read_bytes_cb, _io_write_bytes_cb],
        description="This will show the io read and write bytes of the process",
    )
    meter.create_observable_gauge(
        "process.cpu_affinity.count",
        unit="Count",
        callbacks=[_cpu_affinity_cb],
        description="The will show the cpu affinity of the process",
    )
    meter.create_observable_gauge(
        "process.create_time.timestamp",
        unit="s",
        callbacks=[_create_time_cb],
        description="The will show the create time of the process",
    )
    meter.create_observable_gauge(
        "process.open_files.count",
        unit="Count",
        callbacks=[_open_file_counts_cb],
        description="The will show the open files of the process",
    )
    meter.create_observable_gauge(
        "process.threads.count",
        unit="Count",
        callbacks=[_thread_counts_cb],
        description="The will show the threads of the process",
    )
    meter.create_observable_gauge(
        "process.gc.count",
        unit="Count",
        callbacks=[_gc0_cb, _gc1_cb, _gc2_cb],
        description="The will show the gc of the process",
    )
    meter.create_observable_gauge(
        "process.context_switches.count",
        unit="Count",
        callbacks=[_context_switch_cb],
        description="The will show the context switches of the process",
    )
    meter.create_observable_gauge(
        "process.disk_usage.percentage",
        unit="Percent",
        callbacks=[_disk_usage_percent_cb],
        description="The will show the disk usage percentage of the process",
    )
    meter.create_observable_gauge(
        "process.disk_usage.bytes",
        unit="Bytes",
        callbacks=[_disk_usage_total_cb, _disk_usage_used_cb, _disk_usage_free_cb],
        description="The will show the disk usage of the process",
    )


def _cpu_usage_cb(options: CallbackOptions):
    # print("--- Metrics Generated ---")
    yield Observation(value=psutil.Process(os.getpid()).cpu_percent())


def _ram_usage_cb(options: CallbackOptions):
    yield Observation(value=psutil.Process(os.getpid()).memory_percent())


def _cpu_time_callback(options: CallbackOptions):
    cpu_times = psutil.Process(os.getpid()).cpu_times()
    yield Observation(value=cpu_times.user, attributes={"state": "user"})
    yield Observation(value=cpu_times.system, attributes={"state": "system"})
    yield Observation(
        value=cpu_times.children_user, attributes={"state": "children_user"}
    )
    yield Observation(
        value=cpu_times.children_system, attributes={"state": "children_system"}
    )

    iowait_value = cpu_times.iowait if not psutil.WINDOWS else 0
    yield Observation(value=iowait_value, attributes={"state": "iowait"})


def _memory_rss_cb(options: CallbackOptions):
    yield Observation(
        value=psutil.Process(os.getpid()).memory_info().rss, attributes={"type": "rss"}
    )


def _memory_vms_cb(options: CallbackOptions):
    yield Observation(
        value=psutil.Process(os.getpid()).memory_info().vms, attributes={"type": "vms"}
    )


def _memory_shared_cb(options: CallbackOptions):
    shared_value = (
        psutil.Process(os.getpid()).memory_info().shared if not psutil.WINDOWS else 0
    )
    yield Observation(value=shared_value, attributes={"type": "shared"})


def _memory_text_cb(options: CallbackOptions):
    text_value = (
        psutil.Process(os.getpid()).memory_info().text if not psutil.WINDOWS else 0
    )
    yield Observation(value=text_value, attributes={"type": "text"})


def _memory_data_cb(options: CallbackOptions):
    data_value = (
        psutil.Process(os.getpid()).memory_info().data if not psutil.WINDOWS else 0
    )
    yield Observation(value=data_value, attributes={"type": "data"})


def _num_threads_cb(options: CallbackOptions):
    yield Observation(value=psutil.Process(os.getpid()).num_threads())


def _num_fds_cb(options: CallbackOptions):
    num_fds_value = psutil.Process(os.getpid()).num_fds() if not psutil.WINDOWS else 0
    yield Observation(value=num_fds_value)


def _num_vctx_switches_cb(options: CallbackOptions):
    yield Observation(
        value=psutil.Process(os.getpid()).num_ctx_switches().voluntary,
        attributes={"type": "voluntary"},
    )


def _num_ivctx_switches_cb(options: CallbackOptions):
    yield Observation(
        value=psutil.Process(os.getpid()).num_ctx_switches().involuntary,
        attributes={"type": "involuntary"},
    )


def _num_connections_cb(options: CallbackOptions):
    yield Observation(value=len(psutil.Process(os.getpid()).connections()))


def _io_read_bytes_cb(options: CallbackOptions):
    yield Observation(
        value=psutil.Process(os.getpid()).io_counters().read_bytes,
        attributes={"direction": "read"},
    )


def _io_write_bytes_cb(options: CallbackOptions):
    yield Observation(
        value=psutil.Process(os.getpid()).io_counters().write_bytes,
        attributes={"direction": "write"},
    )


def _cpu_affinity_cb(options: CallbackOptions):
    yield Observation(value=len(psutil.Process(os.getpid()).cpu_affinity()))


def _create_time_cb(options: CallbackOptions):
    yield Observation(value=psutil.Process(os.getpid()).create_time())


def _open_file_counts_cb(options: CallbackOptions):
    yield Observation(value=len(psutil.Process(os.getpid()).open_files()))


def _thread_counts_cb(options: CallbackOptions):
    yield Observation(value=threading.active_count())


def _gc0_cb(options: CallbackOptions):
    yield Observation(value=gc.get_count()[0], attributes={"type": "gc0"})


def _gc1_cb(options: CallbackOptions):
    yield Observation(value=gc.get_count()[1], attributes={"type": "gc1"})


def _gc2_cb(options: CallbackOptions):
    yield Observation(value=gc.get_count()[2], attributes={"type": "gc2"})


def _context_switch_cb(options: CallbackOptions):
    yield Observation(value=getswitchinterval())


def __disk_usage_arr():
    if not psutil.WINDOWS:
        return psutil.disk_usage(os.sep)
    else:
        try:
            return psutil.disk_usage(os.path.abspath(os.sep))
        except Exception as e:
            # Handle any exceptions that may occur
            # print(f"Error: {e}")
            return DiskUsageData(total=0, used=0, free=0, percent=0.0)


def _disk_usage_percent_cb(options: CallbackOptions):
    arr_value = __disk_usage_arr()
    yield Observation(value=arr_value.percent)


def _disk_usage_total_cb(options: CallbackOptions):
    arr_value = __disk_usage_arr()
    yield Observation(value=arr_value.total, attributes={"type": "total"})


def _disk_usage_used_cb(options: CallbackOptions):
    arr_value = __disk_usage_arr()
    yield Observation(value=arr_value.used, attributes={"type": "used"})


def _disk_usage_free_cb(options: CallbackOptions):
    arr_value = __disk_usage_arr()
    yield Observation(value=arr_value.free, attributes={"type": "free"})
