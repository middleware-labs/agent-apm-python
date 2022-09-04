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

from opentelemetry.metrics import get_meter
meter = get_meter("example-meter")
counter = meter.create_counter("example-counter")


server = Server()
server.watch('apmpython.py', delay=5)
server.serve(root='build\lib\apmpython')

class apmpython:
    
    def cpu_usage():
        process = psutil.Process(os.getpid())
        for i in range(10):
            print(process.cpu_percent())
            time.sleep(300)
        

    def ram_usage():
        process = psutil.Process(os.getpid())
        for i in range(10):
            print(process.memory_percent())
            time.sleep(300)

    def disk_usage():
        process = psutil.Process(os.getpid())
        for i in range(10):
            print(process.disk_usage())
            time.sleep(300)
    
    def thread_count():
        print(threading.active_count())
    
    def gen0():
        print(gc.get_count()[0])

    def gen1():
        print(gc.get_count()[1])

    def gen2():
        print(gc.get_count()[2])
    
    def context_switch():
        print(getswitchinterval())


    
  
