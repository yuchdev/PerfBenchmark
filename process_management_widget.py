import warnings
from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QListView, QPushButton, QLabel, QLineEdit, QAbstractItemView
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

        # Line Edit for filtering processes
        self.process_filter_label = QLabel("Filter:")
        self.process_filter_edit = QLineEdit()
        self.process_filter_edit.textChanged.connect(self.update_filtered_processes)

        # Button for adding processes
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.press_add)

        # List Views for filtered processes and selected processes
        self.filter_list_model = QStandardItemModel()
        self.filter_list_view = QListView()
        self.filter_list_view.setModel(self.filter_list_model)
        self.filter_list_view.doubleClicked.connect(self.add_process)

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
        self.process_filter_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.process_filter_label)
        filter_layout.addWidget(self.process_filter_edit)
        filter_layout.addWidget(self.add_button)

        list_layout = QVBoxLayout()
        list_layout.addWidget(self.filter_list_view)
        list_layout.addWidget(self.process_list_view)

        main_layout = QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addLayout(list_layout)
        main_layout.addWidget(self.start_button)

        # Turn off item edit and multiselect
        self.filter_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.process_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filter_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.process_list_view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.setLayout(main_layout)

    def update_filtered_processes(self, text: str):
        """
        Update the filtered processes based on the entered text
        """
        self.filtered_processes = self.cpu_watcher.filter_processes(text)
        extracted_names = [proc['name'] for proc in self.filtered_processes]
        self.filter_list_model.clear()
        for name in extracted_names:
            item = QStandardItem(name)
            self.filter_list_model.appendRow(item)

    def press_add(self):
        """
        Add the selected process from the filtered list to the process list
        Ensure single selection
        """
        selected_index = self.filter_list_view.selectedIndexes()[0] if self.filter_list_view.selectedIndexes() else None
        if selected_index:
            self.add_process(selected_index)

    def add_process(self, index):
        """
        Add the double-clicked process from the filtered list to the process list
        """
        item = self.filter_list_model.itemFromIndex(index)
        process_name = item.text()
        self.process_list_model.appendRow(QStandardItem(process_name))
        self.process_filter_edit.clear()
        self.filter_list_model.clear()

    def start_monitoring(self):
        """
        Reset CPUWatcher and start monitoring the selected processes
        """
        selected_processes = [self.process_list_model.item(i).text() for i in range(self.process_list_model.rowCount())]
        self.cpu_watcher.watched_processes = selected_processes
        self.cpu_watcher.cpu_usage_history = []
        self.process_filter_edit.clear()
        self.process_list_model.clear()
        self.cpu_watcher.start()
