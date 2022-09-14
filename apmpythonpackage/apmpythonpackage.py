from concurrent.futures import process
import psutil
import os
import random
import time
import threading
import gc
from sys import getswitchinterval
""" from ddtrace.runtime import RuntimeMetrics
RuntimeMetrics.enable() """

# from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
# from opentelemetry.metrics import get_meter_provider
# from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
# from opentelemetry.sdk.metrics.measurement import Measurement
from opentelemetry.sdk.metrics.export import (
    HistogramDataPoint,
    Metric,
    MetricExportResult,
    MetricsData,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
    Gauge,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.proto.common.v1.common_pb2 import (
    AnyValue,
    InstrumentationScope,
    KeyValue,
)
from opentelemetry.proto.resource.v1.resource_pb2 import (
    Resource,
)
# from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
# from prometheus_client import Gauge
# from opentelemetry.metrics import get_meter


exporter = OTLPMetricExporter(insecure=True)
# reader = PeriodicExportingMetricReader(exporter)
meter = MeterProvider().get_meter("sample")
todo_gauge = meter.create_observable_gauge("sample")
# set_meter_provider(provider)

# meter = get_meter_provider().get_meter("sample")


class apmpythonclass:  
    def cpu_usage(self):
        process = psutil.Process(os.getpid())
        print("CPU Usage: ",process.cpu_percent())
        attributes = {"cpu_number": str(1)}
        exporter.export(
            MetricsData(
                resource_metrics=[ResourceMetrics(
                    schema_url="",
                    resource=Resource(
                        attributes=[KeyValue(
                            key="a",
                            value=AnyValue(
                                string_value="1"
                            )
                        )],
                        # schema_url="resource_schema_url",
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=InstrumentationScope(
                                name="first name",
                                version="first version"
                            ),
                            schema_url="",
                            metrics=[Metric(
                                name="123",
                                description="456",
                                unit="core",
                                data=Gauge(
                                    data_points=[
                                        NumberDataPoint(
                                            attributes=attributes,
                                            start_time_unix_nano=1641946015139533244,
                                            time_unix_nano=1641946016139533244,
                                            value=random.randint(1, 50),
                                        )
                                    ],
                                )
                            )]
                        )
                    ]
                )]
            )
        )
        # yield Measurement(process.cpu_percent(), todo_gauge, attributes)

    def ram_usage(self):
        process = psutil.Process(os.getpid())
        print("RAM Usage: ",process.memory_percent())
        # todo_gauge.observe(process.memory_percent())

    def disk_usage(self):
        print("Disk Usage: ",psutil.disk_usage(os.sep).percent)
        # todo_gauge.observe(process.disk_usage())

    def thread_count(self):
        print("Thread Count: ",threading.active_count())
        # todo_gauge.observe(threading.active_count())

    def gen0(self):
        print("Gen 0: ",gc.get_count()[0])
        # todo_gauge.observe(gc.get_count()[0])

    def gen1(self):
        print("Gen 1: ",gc.get_count()[1])
        # todo_gauge.observe(gc.get_count()[1])

    def gen2(self):
        print("Gen 2: ",gc.get_count()[2])
        # todo_gauge.observe(gc.get_count()[2])

    def context_switch(self):
        print("Context Switches: ",getswitchinterval())
        # todo_gauge.observe(getswitchinterval())


    def collection(self):
        tracker = apmpythonclass()
        while True:
            tracker.cpu_usage()
            tracker.ram_usage()
            tracker.disk_usage()
            tracker.thread_count()
            tracker.gen0()
            tracker.gen1()
            tracker.gen2()
            tracker.context_switch()
            time.sleep(5)
            print("--------------------------------------------")

tracker = apmpythonclass()
tracker.cpu_usage()
