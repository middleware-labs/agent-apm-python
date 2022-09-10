from concurrent.futures import process
import psutil
import os
import time
import threading
import gc
from sys import getswitchinterval
from ddtrace.runtime import RuntimeMetrics
RuntimeMetrics.enable()

""" from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import get_meter_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import Gauge
from opentelemetry.metrics import get_meter


exporter = OTLPMetricExporter(insecure=True)
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
set_meter_provider(provider)

meter = get_meter_provider().get_meter("sample") """


    
def cpu_usage():
    process = psutil.Process(os.getpid())
    print("CPU Usage: ",process.cpu_percent())
    # todo_gauge.observe(process.cpu_percent())

def ram_usage():
    process = psutil.Process(os.getpid())
    print("RAM Usage: ",process.memory_percent())
    # todo_gauge.observe(process.memory_percent())

def disk_usage():
    print("Disk Usage: ",psutil.disk_usage(os.sep).percent)
    # todo_gauge.observe(process.disk_usage())

def thread_count():
    print("Thread Count: ",threading.active_count())
    # todo_gauge.observe(threading.active_count())

def gen0():
    print("Gen 0: ",gc.get_count()[0])
    # todo_gauge.observe(gc.get_count()[0])

def gen1():
    print("Gen 1: ",gc.get_count()[1])
    # todo_gauge.observe(gc.get_count()[1])

def gen2():
    print("Gen 2: ",gc.get_count()[2])
    # todo_gauge.observe(gc.get_count()[2])

def context_switch():
    print("Context Switches: ",getswitchinterval())
    # todo_gauge.observe(getswitchinterval())


def collection():
    while True:
        cpu_usage()
        ram_usage()
        disk_usage()
        thread_count()
        gen0()
        gen1()
        gen2()
        context_switch()
        time.sleep(5)
        print("--------------------------------------------")
