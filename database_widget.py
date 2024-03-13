import os
import zipfile
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QDialog
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


class DatabaseWidget(QWidget):

    database_name = "CpuMetrics"
    CREATE_CPU_WORKLOAD = "CREATE TABLE IF NOT EXISTS CpuWorkload " \
                          "(ID INTEGER PRIMARY KEY AUTOINCREMENT, " \
                          "Timestamp INTEGER, PID INTEGER, ProcessName TEXT, Workload REAL)"
    CREATE_SYSTEM_EVENTS = "CREATE TABLE IF NOT EXISTS SystemEvents " \
                           "(ID INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp INTEGER, Event TEXT)"
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
        if os.path.isfile(self.database_name):
            self.open_db()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.models_layout = QHBoxLayout(self)

        # Horizontal panel for buttons
        self.button_panel_layout = QHBoxLayout()
        self.create_button("Create", self.create_db)
        self.create_button("Cleanup", self.cleanup_db)
        self.create_button("Backup", self.backup_db)
        self.layout.addLayout(self.button_panel_layout)

        # Table views for CpuWorkload and SystemEvents
        self.cpu_workload_table = QTableView()
        self.system_events_table = QTableView()
        self.models_layout.addWidget(self.cpu_workload_table)
        self.models_layout.addWidget(self.system_events_table)
        self.layout.addLayout(self.models_layout)

        # Column height
        self.cpu_workload_table.verticalHeader().setDefaultSectionSize(10)
        self.system_events_table.verticalHeader().setDefaultSectionSize(10)

    def create_db(self):

        print("Creating database:", self.database_name)
        if os.path.exists(self.database_name) and self.rewrite_database is False:
            print("Database file already exists, exiting")
            return
        elif os.path.exists(self.database_name) and self.rewrite_database is True:
            print("Database file already exists, delete")
            os.remove(self.database_name)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.database_name)
        if not self.db.open():
            print("Failed to create database")
        else:
            print("Database created successfully")
            self.create_tables()
            self.setup_table_models()

    def cleanup_db(self):
        """
        Cleanup all data from the database
        """
        query = QSqlQuery()
        query.exec_("DELETE FROM CpuWorkload")
        query.exec_("DELETE FROM SystemEvents")
        if query.lastError().isValid():
            print("Failed to cleanup database:", query.lastError().text())
        else:
            print("Database cleaned up successfully!")
            self.cpu_workload_model.select()
            self.system_events_model.select()

    def backup_db(self):
        """
        Archive the database file with name CpuMetrics-YYYYMMDD-HHMMSS.zip
        """
        backup_file = f"CpuMetrics-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
        with zipfile.ZipFile(backup_file, "w") as backup:
            backup.write(self.database_name)
        print(f"Database backed up to {backup_file}")

    def open_db(self):
        """
        Open existing SQLite database
        """
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.database_name)
        if not self.db.open():
            print("Failed to open database")
        else:
            print("Database opened successfully")
            self.setup_table_models()

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

        cpu_workload_column_width = (cpu_workload_width / self.cpu_workload_model.columnCount()) * 0.8
        for col in range(self.cpu_workload_model.columnCount()):
            self.cpu_workload_table.setColumnWidth(col, cpu_workload_column_width)

        # Calculate the column width for System Events Table
        system_events_column_width = (system_events_width / self.system_events_model.columnCount()) * 0.8
        for col in range(self.system_events_model.columnCount()):
            self.system_events_table.setColumnWidth(col, system_events_column_width)

    def create_button(self, name, callback):
        button = QPushButton(name)
        button.setFixedWidth(100)
        # noinspection PyUnresolvedReferences
        button.clicked.connect(callback)
        self.button_panel_layout.addWidget(button)

    def create_tables(self):
        query = QSqlQuery()
        query.exec_(self.CREATE_CPU_WORKLOAD)
        query.exec_(self.CREATE_SYSTEM_EVENTS)
        if query.lastError().isValid():
            print("Failed to create tables:", query.lastError().text())
        else:
            print("Tables created successfully!")

    def insert_cpu_workload(self, cpu_usage):
        """
        Inserts a new metric record into the CpuWorkload table
        :param cpu_usage: dictionary containing CPU usage data
        """
        # Prepare the query to insert the record
        query = QSqlQuery()
        query.prepare(
            "INSERT INTO CpuWorkload (Timestamp, PID, ProcessName, Workload) "
            "VALUES (:timestamp, :pid, :process_name, :workload)"
        )
        query.bindValue(":timestamp", cpu_usage['timestamp'])
        query.bindValue(":pid", cpu_usage['pid'])
        query.bindValue(":process_name", cpu_usage['name'])
        query.bindValue(":workload", cpu_usage['usage'])

        # Execute the query
        if not query.exec_():
            print("Failed to insert metric:", query.lastError().text())
        else:
            print("Metric inserted successfully!")

            # Refresh the model to update the view with the new data
            self.cpu_workload_model.select()
