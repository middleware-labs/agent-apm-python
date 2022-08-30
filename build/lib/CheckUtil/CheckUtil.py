import psutil
import os

class CheckUtil:
    
    def cpu_usage():
        process = psutil.Process(os.getpid())
        return process.cpu_percent()

    def ram_usage():
        process = psutil.Process(os.getpid())
        return process.memory_percent()
    
    def disk_usage():
        process = psutil.Process(os.getpid())
        return process.disk_usage()


