import warnings
from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QListView, QPushButton, QComboBox, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from cpu_monitor import CPUWatcher

# Suppress DeprecationWarning for sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning)


# noinspection PyUnresolvedReferences
class ProcessManagementWidget(QWidget):
    """
    Widget for managing the processes to be monitored
    Contains ownership for child widgets, but not for the CPUWatcher object
    """

    def __init__(self, cpu_watcher: CPUWatcher):
        """
        Connect changing of process name and filtering of monitored processes
        QStandardItemModel is chosen for the process list view,
        because it is easier to work with and the list won't be too large
        :param cpu_watcher: a valid CPUWatcher
        """
        super().__init__()
        assert isinstance(cpu_watcher, CPUWatcher)
        self.cpu_watcher = cpu_watcher
        self.filtered_processes = []
        self.debug_call_depth = 0

        # Dropdown for filtering processes
        self.process_filter_label = QLabel("Filter:")
        self.process_filter_combobox = QComboBox()
        self.process_filter_combobox.setEditable(True)
        self.process_filter_combobox.lineEdit().textChanged.connect(self.update_filtered_processes)

        # 'Add' button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_process)

        # Process list
        self.process_list_model = QStandardItemModel()
        self.process_list_view = QListView()
        self.process_list_view.setModel(self.process_list_model)

        # 'Start Monitoring' button
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)

        self.init_ui()

    def init_ui(self):
        """
        Set up the layout and geometry of the widget
        Set size policy for widgets to maintain their size on resizing
        """
        process_filter_layout = QHBoxLayout()

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

    def update_filtered_processes(self, text: str):
        """
        Update the filtered processes based on the entered text
        Every time we have to reconnect the textChanged signal,
        because otherwise the signal will be emitted indefinitely
        """
        assert isinstance(text, str)
        # Disconnect the textChanged signal temporarily
        self.process_filter_combobox.lineEdit().textChanged.disconnect(self.update_filtered_processes)

        # Update filtered processes based on the entered text
        self.filtered_processes = self.cpu_watcher.filter_processes(text)
        extracted_names = [proc['name'] for proc in self.filtered_processes]

        # Clear the current items and add the extracted process names
        self.process_filter_combobox.clear()
        self.process_filter_combobox.addItems(extracted_names)

        # Open the dropdown if there is more than one item
        if len(extracted_names) > 1:
            self.process_filter_combobox.showPopup()

        # Reconnect the textChanged signal
        self.process_filter_combobox.lineEdit().textChanged.connect(self.update_filtered_processes)

    def add_process(self):
        """
        Create a new item and add it to the model
        """
        process_name = self.process_filter_combobox.currentText()
        if process_name:
            item = QStandardItem(process_name)
            self.process_list_model.appendRow(item)

    def start_monitoring(self):
        """
        Reset CPUWatcher and start monitoring the selected processes
        """
        selected_processes = [self.process_list_view.model().item(i).text() for i in range(self.process_list_view.model().rowCount())]
        self.cpu_watcher.watched_processes = selected_processes
        self.cpu_watcher.cpu_usage_history = []
        self.cpu_watcher.start()
