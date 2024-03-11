import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QDialogButtonBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QHeaderView


class DatabaseWidget(QWidget):
    CREATE_CPU_WORKLOAD = "CREATE TABLE IF NOT EXISTS CpuWorkload " \
                          "(ID INTEGER PRIMARY KEY AUTOINCREMENT, " \
                          "Timestamp INTEGER, PID INTEGER, ProcessName TEXT, Workload REAL)"
    CREATE_SYSTEM_EVENTS = "CREATE TABLE IF NOT EXISTS SystemEvents " \
                           "(ID INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp TEXT, Event TEXT)"
    INSERT_CPU_WORKLOAD = "INSERT INTO CpuWorkload (Timestamp, PID, ProcessName, Workload) " \
                          "VALUES (:timestamp, :pid, :process_name, :workload)"

    def __init__(self, rewrite_database):
        super().__init__()
        self.models_layout = None
        self.cpu_workload_table = None
        self.system_events_table = None
        self.button_panel_layout = None
        self.layout = None
        self.db = None
        self.rewrite_database = rewrite_database
        self.cpu_workload_model = QSqlTableModel()
        self.system_events_model = QSqlTableModel()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.models_layout = QHBoxLayout(self)

        # Horizontal panel for buttons
        self.button_panel_layout = QHBoxLayout()
        self.create_button("Create", self.create_db)
        self.create_button("Insert", self.test_insert)
        self.layout.addLayout(self.button_panel_layout)

        # Table views for CpuWorkload and SystemEvents
        self.cpu_workload_table = QTableView()
        self.system_events_table = QTableView()
        self.models_layout.addWidget(self.cpu_workload_table)
        self.models_layout.addWidget(self.system_events_table)
        self.layout.addLayout(self.models_layout)

        # Set up the database models
        self.cpu_workload_model.setTable("CpuWorkload")
        self.cpu_workload_model.select()
        self.system_events_model.setTable("SystemEvents")
        self.system_events_model.select()

        # Set models for table views
        self.cpu_workload_table.setModel(self.cpu_workload_model)
        self.system_events_table.setModel(self.system_events_model)

        # Adjust column widths
        for view in [self.cpu_workload_table, self.system_events_table]:
            header = view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def create_button(self, name, callback):
        button = QPushButton(name)
        button.setFixedWidth(100)
        # noinspection PyUnresolvedReferences
        button.clicked.connect(callback)
        self.button_panel_layout.addWidget(button)

    def create_db(self):
        name = "CpuMetrics"
        if os.path.exists(name) and self.rewrite_database is False:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(name)
            if not self.db.open():
                print("Failed to open database!")
                return
            else:
                print("Database opened successfully!")
                # Setup table models after database open
                self.setup_table_models()
                return

        dialog = QDialog(self)
        dialog.setWindowTitle("Create Database")
        layout = QVBoxLayout()

        label = QLabel("Database Name:")
        edit = QLineEdit(name)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        def create():
            db_name = edit.text()
            if os.path.exists(db_name) and self.rewrite_database is False:
                print("Database file already exists, exiting")
                dialog.reject()
                return
            elif os.path.exists(db_name) and self.rewrite_database is True:
                print("Database file already exists, delete")
                os.remove(db_name)

            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(db_name)
            if not self.db.open():
                print("Failed to create database!")
            else:
                print("Database created successfully!")
                self.create_tables()
                self.setup_table_models()  # Setup table models after database creation
                dialog.accept()

        # noinspection PyUnresolvedReferences
        buttons.accepted.connect(create)
        # noinspection PyUnresolvedReferences
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(label)
        layout.addWidget(edit)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def setup_table_models(self):
        # Set up table models
        self.cpu_workload_model = QSqlTableModel()
        self.system_events_model = QSqlTableModel()
        self.cpu_workload_model.setTable("CpuWorkload")
        self.system_events_model.setTable("SystemEvents")
        self.cpu_workload_model.select()
        self.system_events_model.select()

        # Set models for table views
        self.cpu_workload_table.setModel(self.cpu_workload_model)
        self.system_events_table.setModel(self.system_events_model)

        # Get the width of each TableView
        cpu_workload_width = self.cpu_workload_table.width()
        system_events_width = self.system_events_table.width()

        # Calculate the column width for CPU Workload Table
        cpu_workload_column_width = cpu_workload_width / self.cpu_workload_model.columnCount()
        for col in range(self.cpu_workload_model.columnCount()):
            self.cpu_workload_table.setColumnWidth(col, cpu_workload_column_width)

        # Calculate the column width for System Events Table
        system_events_column_width = system_events_width / self.system_events_model.columnCount()
        for col in range(self.system_events_model.columnCount()):
            self.system_events_table.setColumnWidth(col, system_events_column_width)

    def create_tables(self):
        query = QSqlQuery()
        query.exec_(self.CREATE_CPU_WORKLOAD)
        query.exec_(self.CREATE_SYSTEM_EVENTS)
        if query.lastError().isValid():
            print("Failed to create tables:", query.lastError().text())
        else:
            print("Tables created successfully!")

    def insert_metric(self, cpu_usage_history):
        """
        Inserts a new metric record into the CpuWorkload table
        :param cpu_usage_history: dictionary containing CPU usage data
        """
        # Prepare the query to insert the record
        cpu_usage = cpu_usage_history[-1]
        query = QSqlQuery()
        query.prepare(
            "INSERT INTO CpuWorkload (Timestamp, PID, ProcessName, Workload) "
            "VALUES (:timestamp, :pid, :process_name, :workload)"
        )
        query.bindValue(":timestamp", cpu_usage['timestamp'])
        query.bindValue(":pid", cpu_usage['pid'])
        query.bindValue(":process_name", cpu_usage['process_name'])
        query.bindValue(":workload", cpu_usage['workload'])

        # Execute the query
        if not query.exec_():
            print("Failed to insert metric:", query.lastError().text())
        else:
            print("Metric inserted successfully!")

            # Refresh the model to update the view with the new data
            self.cpu_workload_model.select()

    def test_insert(self):
        test_cpu_payload = [
            {"timestamp": 1, "pid": 1, "process_name": "test1", "workload": 1.1},
        ]
        self.insert_cpu_workload(test_cpu_payload)
