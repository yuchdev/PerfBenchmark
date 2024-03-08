import os

from PyQt5.QtCore import Qt
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
    DATABASE_FILE = "CpuMetrics"

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
        self.setup_database()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.models_layout = QHBoxLayout(self)

        # Horizontal panel for buttons
        self.button_panel_layout = QHBoxLayout()
        self.create_button("Create", self.create_database)
        self.create_button("Import", None)  # Replace with None
        self.create_button("Export", None)  # Replace with None
        self.create_button("Cleanup", None)  # Replace with None
        self.create_button("Drop", None)  # Replace with None
        self.create_button("Backup", None)  # Replace with None
        self.layout.addLayout(self.button_panel_layout)

        # Table views for CpuWorkload and SystemEvents
        self.cpu_workload_table = QTableView()
        self.system_events_table = QTableView()
        self.models_layout.addWidget(self.cpu_workload_table)
        self.models_layout.addWidget(self.system_events_table)
        self.layout.addLayout(self.models_layout)

        # Adjust column widths
        for view in [self.cpu_workload_table, self.system_events_table]:
            header = view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def setup_database(self):
        """
        Set up the database, either by loading it from the file or creating a new one
        """
        if os.path.exists(self.DATABASE_FILE):
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(self.DATABASE_FILE)
            if not self.db.open():
                print("Failed to open database!")
                return
            print("Database opened successfully!")

            # Set models for table views
            self.cpu_workload_model.setTable("CpuWorkload")
            self.system_events_model.setTable("SystemEvents")
            self.cpu_workload_model.select()
            self.system_events_model.select()

            # Ensure that model data is fetched
            self.cpu_workload_model.fetchAll()
            self.system_events_model.fetchAll()

            self.cpu_workload_table.setModel(self.cpu_workload_model)
            self.system_events_table.setModel(self.system_events_model)

            # Set headers
            self.set_table_headers(self.cpu_workload_model, self.cpu_workload_table)
            self.set_table_headers(self.system_events_model, self.system_events_table)
        else:
            print("Database file not found, creating new database...")

    def set_table_headers(self, model, table_view):
        """
        Set table headers based on the model
        """
        header = table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        for i in range(model.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(i, QHeaderView.Interactive)
            header.setStretchLastSection(False)
            header.setSortIndicatorShown(True)
            header.setSortIndicator(i, Qt.AscendingOrder)
            header.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            header.setSectionHidden(i, False)

    def create_button(self, name, callback):
        button = QPushButton(name)
        button.setFixedWidth(100)
        self.button_panel_layout.addWidget(button)
        if callback:
            button.clicked.connect(callback)

    def create_database(self):
        if os.path.exists(self.DATABASE_FILE) and not self.rewrite_database:
            self.setup_database()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Create Database")
        layout = QVBoxLayout()

        label = QLabel("Database Name:")
        edit = QLineEdit(self.DATABASE_FILE)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        def create():
            db_name = edit.text()
            if os.path.exists(db_name) and not self.rewrite_database:
                print("Database file already exists, exiting")
                dialog.reject()
                return
            elif os.path.exists(db_name) and self.rewrite_database:
                print("Database file already exists, delete")
                os.remove(db_name)

            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(db_name)
            if not self.db.open():
                print("Failed to create database!")
            else:
                print("Database created successfully!")
                self.create_tables()
                self.setup_database()
                dialog.accept()

        buttons.accepted.connect(create)
        buttons.rejected.connect(dialog.reject)

        self.setup_database()

        layout.addWidget(label)
        layout.addWidget(edit)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def create_tables(self):
        query = QSqlQuery()
        query.exec_(self.CREATE_CPU_WORKLOAD)
        query.exec_(self.CREATE_SYSTEM_EVENTS)
        if query.lastError().isValid():
            print("Failed to create tables:", query.lastError().text())
        else:
            print("Tables created successfully!")

    def insert_cpu_workload(self, cpu_workload):
        timestamp = cpu_workload['timestamp']
        pid = cpu_workload['pid']
        process_name = cpu_workload['process_name']
        workload = cpu_workload['workload']
        query = QSqlQuery()
        query.prepare(self.INSERT_CPU_WORKLOAD)
        query.bindValue(":timestamp", timestamp)
        query.bindValue(":pid", pid)
        query.bindValue(":process_name", process_name)
        query.bindValue(":workload", workload)

        if not query.exec_():
            print("Failed to insert metric:", query.lastError().text())
        else:
            print("Metric inserted successfully!")
            self.cpu_workload_model.select()