import threading
from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QLabel
import warnings

# Suppress DeprecationWarning for sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning)


# noinspection PyUnresolvedReferences
class ProcessManagementWidget(QWidget):
    def __init__(self, cpu_watcher):
        super().__init__()
        self.cpu_watcher_thread = None
        self.cpu_watcher = cpu_watcher
        self.filtered_processes = []
        self.debug_call_depth = 0

        self.process_filter_label = QLabel("Filter:")
        self.process_filter_combobox = QComboBox()
        self.process_filter_combobox.setEditable(True)
        self.process_filter_combobox.lineEdit().textChanged.connect(self.update_filtered_processes)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_process)

        self.process_list_view = QListView()

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)

        self.init_ui()

    def init_ui(self):
        self.debug_print("init_ui()")
        process_filter_layout = QHBoxLayout()
        process_filter_layout.addWidget(self.process_filter_label)
        process_filter_layout.addWidget(self.process_filter_combobox)
        process_filter_layout.addWidget(self.add_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(process_filter_layout)
        main_layout.addWidget(self.process_list_view)
        main_layout.addWidget(self.start_button)

        self.setLayout(main_layout)

    def update_filtered_processes(self, text):
        self.debug_print("update_filtered_processes()")
        # Update filtered processes based on the entered text
        self.filtered_processes = self.cpu_watcher.filter_processes(text)
        extracted_names = [proc['name'] for proc in self.filtered_processes]
        self.process_filter_combobox.clear()
        self.process_filter_combobox.addItems(extracted_names)

    def add_process(self):
        self.debug_print("add_process()")
        process_name = self.process_filter_combobox.currentText()
        if process_name:
            self.process_list_view.model().insertRow(self.process_list_view.model().rowCount())
            index = self.process_list_view.model().index(self.process_list_view.model().rowCount() - 1, 0)
            self.process_list_view.model().setData(index, process_name)

    def start_monitoring(self):
        self.debug_print("start_monitoring()")
        selected_processes = [self.process_list_view.model().item(i).text() for i in range(self.process_list_view.model().rowCount())]
        self.cpu_watcher.watched_processes = selected_processes
        self.cpu_watcher.cpu_usage_history = []
        self.cpu_watcher_thread = threading.Thread(target=self.cpu_watcher.watch)
        self.cpu_watcher_thread.start()

    def debug_print(self, message):
        print("  " * self.debug_call_depth + message)
        self.debug_call_depth += 1
