from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import warnings

# Suppress DeprecationWarning for sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning)


# noinspection PyUnresolvedReferences
class ProcessManagementWidget(QWidget):
    def __init__(self, cpu_watcher):
        super().__init__()
        self.cpu_watcher = cpu_watcher
        self.filtered_processes = []
        self.debug_call_depth = 0

        self.process_filter_label = QLabel("Filter:")
        self.process_filter_combobox = QComboBox()
        self.process_filter_combobox.setEditable(True)
        self.process_filter_combobox.lineEdit().textChanged.connect(self.update_filtered_processes)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_process)

        # Create a QStandardItemModel
        self.process_list_model = QStandardItemModel()

        self.process_list_view = QListView()
        self.process_list_view.setModel(self.process_list_model)

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)

        self.init_ui()

    def init_ui(self):
        process_filter_layout = QHBoxLayout()

        # Set size policy for QLabel and QPushButton to maintain their size
        self.process_filter_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        process_filter_layout.addWidget(self.process_filter_label)
        process_filter_layout.addWidget(self.process_filter_combobox, stretch=1)  # Add stretch factor to QComboBox
        process_filter_layout.addWidget(self.add_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(process_filter_layout)
        main_layout.addWidget(self.process_list_view)
        main_layout.addWidget(self.start_button)

        self.setLayout(main_layout)

    def update_filtered_processes(self, text):
        # Disconnect the textChanged signal temporarily
        self.process_filter_combobox.lineEdit().textChanged.disconnect(self.update_filtered_processes)

        # Update filtered processes based on the entered text
        self.filtered_processes = self.cpu_watcher.filter_processes(text)
        extracted_names = [proc['name'] for proc in self.filtered_processes]

        # Clear the current items and add the extracted names
        self.process_filter_combobox.clear()
        self.process_filter_combobox.addItems(extracted_names)

        # Open the dropdown if there is more than one item
        if len(extracted_names) > 1:
            self.process_filter_combobox.showPopup()

        # Reconnect the textChanged signal
        self.process_filter_combobox.lineEdit().textChanged.connect(self.update_filtered_processes)

    def add_process(self):
        process_name = self.process_filter_combobox.currentText()
        if process_name:
            # Create a new item and add it to the model
            item = QStandardItem(process_name)
            self.process_list_model.appendRow(item)

    def start_monitoring(self):
        print("start_monitoring()")
        selected_processes = [self.process_list_view.model().item(i).text() for i in range(self.process_list_view.model().rowCount())]
        self.cpu_watcher.watched_processes = selected_processes
        print(f'={self.cpu_watcher.watched_processes}')
        self.cpu_watcher.cpu_usage_history = []
        self.cpu_watcher.start()
