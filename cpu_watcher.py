
import time
import psutil

from PyQt5.QtCore import QThread, pyqtSignal


# noinspection PyUnresolvedReferences
class CPUWatcher(QThread):
    """
    The class collects real-time data on CPU performance for certain processes
    Allows passing the data to consumers using Qt signals and slots
    """

    # Signals are used to communicate between threads
    stopped = pyqtSignal()
    new_data = pyqtSignal(list)
    insert_record = pyqtSignal(dict)

    def __init__(self, watched_processes, interval=1, parent=None):
        """
        :param watched_processes: Processes whose CPU load we monitor
        :param interval: ticks in seconds
        :param parent: parent object
        """
        super().__init__(parent)
        self.is_running = True
        self.is_paused = False  # Flag to indicate if the thread is paused
        self.watched_processes = watched_processes
        self.interval = interval
        self.process_dict = {}  # Dictionary to store process information
        self.cpu_usage_history = []
        self.is_running = True

    def get_processes(self):
        """
        We call this method every time we need an up-to-date list of processes
        Either for filtering or for monitoring
        :return: list of dicts with process id and name
        """
        if not self.process_dict:
            self.process_dict = {
                proc.info['pid']: proc.info['name'] for proc in psutil.process_iter(['pid', 'name'])
            }
        return self.process_dict

    def filter_processes(self, filter_str):
        """
        Filter processes by beginning of string
        Can return several different processes with the same name
        :param filter_str: Filter input, e.g., 'expl'
        :return: list of dicts with process id and name
        """
        process_dict = self.get_processes()
        if not filter_str:
            return process_dict
        return {pid: name for pid, name in process_dict.items() if name.startswith(filter_str)}

    def run(self):
        """
        Main method of the Qt thread
        For Qt widgets prefer it over Python's built-in threading module
        """
        while self.is_running:
            while self.is_paused:  # Check if the thread is paused
                time.sleep(1)
            cpu_usage = self.get_cpu_usage()
            self.cpu_usage_history.append(cpu_usage)
            self.new_data.emit(self.cpu_usage_history)

            # repack CPU usage data to be inserted into the database:
            # {pid: (usage, timestamp)} -> {pid: (usage, timestamp, name)}
            for pid, (usage, timestamp) in cpu_usage.items():
                process_name = self.process_dict[pid]
                self.insert_record.emit(
                    {'pid': pid, 'usage': usage, 'timestamp': timestamp, 'name': process_name}
                )

            time.sleep(self.interval)
        self.stopped.emit()

    def get_cpu_usage(self):
        """
        Get CPU usage for watched processes
        Real usage may exceed 100% if there are more than one core,
        we normalize it to 100% by dividing by the number of cores
        :return: dictionary
        """
        cpu_usage = {}
        num_cores = psutil.cpu_count()
        watched_processes = [
            pid for pid, name in self.get_processes().items() if name in self.watched_processes
        ]
        timestamp = time.time()
        for pid in watched_processes:
            try:
                process = psutil.Process(pid)
                usage_percent = process.cpu_percent(interval=self.interval)
                usage_normalized = usage_percent / num_cores
                cpu_usage[pid] = (usage_normalized, timestamp)
            except psutil.NoSuchProcess:
                cpu_usage[pid] = None
        print(f'cpu_usage={cpu_usage}')
        return cpu_usage

    def stop(self):
        self.is_running = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
