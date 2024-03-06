import psutil
import time
import argparse
from PyQt5.QtCore import QThread, pyqtSignal

__doc__ = """Collect real-time data on CPU performance for certain processes
Allows passing the data to consumers using pipelines
"""


# noinspection PyUnresolvedReferences
class CPUWatcher(QThread):
    stopped = pyqtSignal()
    new_data = pyqtSignal(list)

    def __init__(self, watched_processes, interval=1, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.watched_processes = watched_processes
        self.interval = interval
        self.process_list = []
        self.cpu_usage_history = []
        self.is_running = True

    def get_processes(self):
        if not self.process_list:
            self.process_list = [
                {'pid': proc.info['pid'], 'name': proc.info['name']} for proc in psutil.process_iter(['pid', 'name'])
            ]
        return self.process_list

    def filter_processes(self, filter_str):
        process_list = self.get_processes()
        if not filter_str:
            return process_list
        return [proc for proc in process_list if proc['name'].startswith(filter_str)]

    def run(self):
        while self.is_running:
            cpu_usage = self.get_cpu_usage()
            self.cpu_usage_history.append(cpu_usage)
            self.new_data.emit(self.cpu_usage_history)
            time.sleep(self.interval)
        self.stopped.emit()

    def get_cpu_usage(self):
        cpu_usage = {}
        num_cores = psutil.cpu_count()
        watched_processes = [proc['pid'] for proc in self.get_processes() if proc['name'] in self.watched_processes]
        for pid in watched_processes:
            try:
                process = psutil.Process(pid)
                usage_percent = process.cpu_percent(interval=self.interval)
                usage_normalized = usage_percent / num_cores
                cpu_usage[pid] = usage_normalized
            except psutil.NoSuchProcess:
                cpu_usage[pid] = None
        print(f'cpu_usage={cpu_usage}')
        return cpu_usage

    def stop(self):
        self.is_running = False


def main():
    parser = argparse.ArgumentParser(description="Watch CPU usage of specified processes")
    parser.add_argument('--processes', '-p',
                        metavar='ProcessName',
                        type=str,
                        nargs='+',
                        help='Name of the processes to monitor')
    parser.add_argument('--interval', '-i',
                        type=int,
                        default=5,
                        help='Interval in seconds between each check (default: 5)')
    args = parser.parse_args()

    watcher = CPUWatcher(args.processes, args.interval)
    watcher.watch()


if __name__ == "__main__":
    main()
