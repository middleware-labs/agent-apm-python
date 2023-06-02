from concurrent.futures import process
# import psutil
import os
import time
import pyroscope
import threading
import gc
import requests, json
from sys import getswitchinterval
from fluent import sender
import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

pid = os.getpid()
default_project_name = "Project-" + str(pid)
default_service_name = "Service-" + str(pid)

mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')
logger = sender.FluentSender('app', host=mw_agent_target, port=8006)

from opentelemetry import trace

class apmpythonclass:
    def cpu_usage(self):
        print("cpu usage")
        # process = psutil.Process(os.getpid())
        # print("CPU Usage: ", process.cpu_percent())
        # todo_gauge.observe(process.cpu_percent())

    def ram_usage(self):
        print("ram usage")
        # process = psutil.Process(os.getpid())
        # print("RAM Usage: ", process.memory_percent())
        # todo_gauge.observe(process.memory_percent())

    def disk_usage(self):
        print("disk usage")
        # print("Disk Usage: ", psutil.disk_usage(os.sep).percent)
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


    def severitylog(self, severity, message):
        logger.emit(default_project_name, {
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
    def mw_tracer(self, project_name=default_project_name, service_name=default_service_name, access_token="", enabledProfiling=True):

        # Profiling application, if enabled
        if enabledProfiling and access_token != "":
            
            # Setting Middleware Account Authentication URL
            authUrl = os.getenv('MW_AUTH_URL', 'https://app.middleware.io/api/v1/auth')

            # Setting Middleware Profiling Server URL
            profilingServerUrl = os.getenv('MW_PROFILING_SERVER_URL', 'https://profiling.middleware.io')

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                # "Authorization": "Bearer " + c.accessToken
                "Authorization": "Bearer " + access_token
            }
            try:
                response = requests.post(authUrl, headers=headers)

                # Checking if auth API returns status code 200
                if response.status_code == 200:
                    data = json.loads(response.text)

                    # Checking if a tenantID could be fetched from API Key
                    if data["success"]:
                        account = data["data"]["account"] 
                        pyroscope.configure(
                            application_name = service_name, # replace this with some name for your application
                            server_address   = profilingServerUrl, # replace this with the address of your pyroscope server
                            tenant_id=account,
                        )
                    else:
                        print("Request failed: " + data["error"])
                else:
                    print("Request failed with status code: " + str(response.status_code))
            except Exception as e:
                print("Error making request:", e)
        else:
            print("Profiling is not enabled or access token is empty")

        
        # Setting values for tracing application
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


    def mw_handler  (self):
        logger_provider = LoggerProvider(
            resource=Resource.create(
                {
                    "service.name": default_service_name,
                    'project.name': default_project_name
                }
            ),
        )
        set_logger_provider(logger_provider)
        exporter = OTLPLogExporter(insecure=True,endpoint=mw_agent_target+":9319")
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        return handler

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
