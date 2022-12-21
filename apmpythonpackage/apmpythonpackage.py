from concurrent.futures import process
import psutil
import os
import time
import threading
import gc
from sys import getswitchinterval
from fluent import sender
from opentelemetry.sdk.resources import Resource

pid = os.getpid()
default_project_name = "Project-" + str(pid)
default_service_name = "Service-" + str(pid)

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
        print("CPU Usage: ", process.cpu_percent())
        # todo_gauge.observe(process.cpu_percent())

    def ram_usage(self):
        process = psutil.Process(os.getpid())
        print("RAM Usage: ", process.memory_percent())
        # todo_gauge.observe(process.memory_percent())

    def disk_usage(self):
        print("Disk Usage: ", psutil.disk_usage(os.sep).percent)
        # todo_gauge.observe(process.disk_usage())

    def thread_count(self):
        print("Thread Count: ", threading.active_count())
        # todo_gauge.observe(threading.active_count())

    def gen0(self):
        print("Gen 0: ", gc.get_count()[0])
        # todo_gauge.observe(gc.get_count()[0])

    def gen1(self):
        print("Gen 1: ", gc.get_count()[1])
        # todo_gauge.observe(gc.get_count()[1])

    def gen2(self):
        print("Gen 2: ", gc.get_count()[2])
        # todo_gauge.observe(gc.get_count()[2])

    def context_switch(self):
        print("Context Switches: ", getswitchinterval())
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
    # def logemit(self, arg1, arg2):
    #     logger.emit(arg1, arg2)

    def severitylog(self, severity, message):
        logger.emit('python-apm', {
            'level': severity,
            'message': message,
            'project.name': default_project_name,
            'service.name': default_service_name
        })

    def error(self, error):
        self.severitylog('error', error)
        
    def info(self, info):
        self.severitylog('info', info)

    def warn(self, warn):
        self.severitylog('warn', warn)

    def debug(self, debug):
        self.severitylog('debug', debug)

    # tracing method
    def mw_tracer(self, project_name=default_project_name, service_name=default_service_name):
        if type(project_name) is not str:
            print("project name must be a string")
            return
        if type(service_name) is not str:
            print("service name must be a string")
            return
        global default_project_name 
        default_project_name = str(project_name)
        global default_service_name 
        default_service_name = str(service_name)
        trace.set_tracer_provider(TracerProvider(resource=Resource.create({
            "service.name": service_name,
            "project.name": project_name,
        })))
        tracer = trace.get_tracer_provider().get_tracer(__name__)
        otlp_exporter = OTLPSpanExporter(endpoint=mw_agent_target + ":9319", insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(
            span_processor)
        return tracer, trace, extract, collect_request_attributes

    def record_error(self, error):
        span = trace.get_current_span()
        span.record_exception(error)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))

    def set_attribute(self, name, value):
        if type(name) is not str:
            print("name must be a string")
            return
        if type(value) is not str:
            print("value must be a string")
            return
        span = trace.get_current_span()
        span.set_attribute(name, value)
