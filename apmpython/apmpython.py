from concurrent.futures import process
import psutil
import os
import time
import threading
import gc
from sys import getswitchinterval
from livereload import Server, shell
from ddtrace.runtime import RuntimeMetrics
RuntimeMetrics.enable()

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import (get_meter_provider,set_meter_provider,)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import Gauge
from opentelemetry.metrics import get_meter


exporter = OTLPMetricExporter(insecure=True)
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
set_meter_provider(provider)

meter = get_meter_provider().get_meter("sample")

# todo_gauge = meter.create_observable_gauge(name="sample",unit="0.1.2")


server = Server()
server.watch('apmpython.py', delay=5)
server.serve(root='build\lib\apmpython')

class apmpython:
    
    def cpu_usage():
        process = psutil.Process(os.getpid())
        for i in range(10):
            print(process.cpu_percent())
            time.sleep(300)
            todo_gauge.observe(process.cpu_percent())

   

    def ram_usage():
        process = psutil.Process(os.getpid())
        for i in range(10):
            print(process.memory_percent())
            time.sleep(300)
            todo_gauge.observe(process.memory_percent())

    def disk_usage():
        process = psutil.Process(os.getpid())
        for i in range(10):
            print(process.disk_usage())
            time.sleep(300)
            todo_gauge.observe(process.disk_usage())
    
    def thread_count():
        print(threading.active_count())
        todo_gauge.observe(threading.active_count())
    
    def gen0():
        print(gc.get_count()[0])
        todo_gauge.observe(gc.get_count()[0])

    def gen1():
        print(gc.get_count()[1])
        todo_gauge.observe(gc.get_count()[1])

    def gen2():
        print(gc.get_count()[2])
        todo_gauge.observe(gc.get_count()[2])
    
    def context_switch():
        print(getswitchinterval())
        todo_gauge.observe(getswitchinterval())


    
  
