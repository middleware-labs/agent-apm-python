from concurrent.futures import process
import psutil
import os
import time
import threading
import gc
from sys import getswitchinterval
from fluent import sender

mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')
logger = sender.FluentSender('app', host=mw_agent_target, port=8006)

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.wsgi import collect_request_attributes
from opentelemetry.propagate import extract
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


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

    def collect(self):
        t1 = threading.Thread(target=self.collection)
        t1.start()

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

    # logs method
    def logemit(self, arg1, arg2):
        logger.emit(arg1, arg2)

    # tracing method
    def mw_tracer(self):
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer_provider().get_tracer(__name__)
        otlp_exporter = OTLPSpanExporter(endpoint=mw_agent_target + ":9319", insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(
            span_processor)
        return tracer, trace, extract, collect_request_attributes
