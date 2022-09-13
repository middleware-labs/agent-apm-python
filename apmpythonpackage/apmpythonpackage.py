from concurrent.futures import process
import psutil
import os
import time
import threading
import gc
from sys import getswitchinterval
<<<<<<< HEAD
from fluent import sender
# from ddtrace.runtime import RuntimeMetrics
# RuntimeMetrics.enable()

# from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
# from opentelemetry.metrics import get_meter_provider
# from opentelemetry.metrics import set_meter_provider
# from opentelemetry.sdk.metrics import MeterProvider
# from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
# from prometheus_client import Gauge
# from opentelemetry.metrics import get_meter


# exporter = OTLPMetricExporter(insecure=True)
# reader = PeriodicExportingMetricReader(exporter)
# provider = MeterProvider(metric_readers=[reader])
# set_meter_provider(provider)

=======
<<<<<<< HEAD:apmpython/apmpython.py
from fluent import sender
# from ddtrace.runtime import RuntimeMetrics
# RuntimeMetrics.enable()
=======
from ddtrace.runtime import RuntimeMetrics
RuntimeMetrics.enable()

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import get_meter_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import Gauge
from opentelemetry.metrics import get_meter
>>>>>>> 7a3d3327e25943e26a1ffeb77fdd0f294d0797b1:apmpythonpackage/apmpythonpackage.py


# from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
# from opentelemetry.metrics import (get_meter_provider,set_meter_provider,)
# from opentelemetry.sdk.metrics import MeterProvider
# from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
# from prometheus_client import Gauge
# from opentelemetry.metrics import get_meter


# exporter = OTLPMetricExporter(insecure=True)
# reader = PeriodicExportingMetricReader(exporter)
# provider = MeterProvider(metric_readers=[reader])
# set_meter_provider(provider)

>>>>>>> 0d2e6a61b4395dfcc93fe6b00ca9fd5e5608a69e
# meter = get_meter_provider().get_meter("sample")

class apmpythonclass:  
    def cpu_usage(self):
        process = psutil.Process(os.getpid())
        print("CPU Usage: ",process.cpu_percent())
        # todo_gauge.observe(process.cpu_percent())

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


<<<<<<< HEAD:apmpython/apmpython.py
def collection():

    tracker = apmpython()
    i=0
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
        i=1+1
        if i > 10:
            break

def logemit(arg1, arg2):
    logger = sender.FluentSender('app', host='localhost', port=8006)
    logger.emit(arg1, arg2)




    
  
=======
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
<<<<<<< HEAD

    
    def logemit(arg1, arg2):
        logger = sender.FluentSender('app', host='localhost', port=8006)
        logger.emit(arg1, arg2)
=======
>>>>>>> 7a3d3327e25943e26a1ffeb77fdd0f294d0797b1:apmpythonpackage/apmpythonpackage.py
>>>>>>> 0d2e6a61b4395dfcc93fe6b00ca9fd5e5608a69e
