import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QTabWidget, QVBoxLayout, QAction

from process_management_widget import ProcessManagementWidget
from cpu_chart_widget import CPUChartWidget
from cpu_watcher import CPUWatcher
from database_widget import DatabaseWidget
from settings_widget import SettingsWidget, DEFAULT_SETTINGS


def appdata_local_path():
    """
    Get the path to the local app data folder
    :return: str
    """
    return os.path.join(os.getenv('LOCALAPPDATA'), "cpu-usage-monitor")


# noinspection PyPep8Naming
class MainWindow(QMainWindow):
    """
    Application main window
    Assume width 90% of screen width and height 80% of screen height
    """

    SETTINGS_FILENAME = "settings.json"

    def __init__(self, cpu_watcher: CPUWatcher):
        """
        Contains ownership for child widgets, but not for the CPUWatcher object
        Connects the CPUWatcher to the CPUChartWidget to update the chart
        :param cpu_watcher:
        """
        super().__init__()
        assert isinstance(cpu_watcher, CPUWatcher)
        self.setWindowTitle("CPU Usage Monitor")

        # Main window geometry
        desktop = QApplication.desktop()
        screen_width = desktop.width()
        screen_height = desktop.height()
        self.setGeometry(20, 20, int(screen_width * 0.9), int(screen_height * 0.8))
        self.settings = None
        self.settings_file = os.path.join(appdata_local_path(), self.SETTINGS_FILENAME)

        self.load_settings()

        # Widgets
        self.cpu_watcher = cpu_watcher
        self.cpu_chart_widget = CPUChartWidget(self)
        self.process_management_widget = ProcessManagementWidget(cpu_watcher)
        self.database_widget = DatabaseWidget(self.settings['rewrite_database'])

        # Create tabs
        tab_widget = QTabWidget()

        # Create Monitoring tab
        monitoring_tab = QWidget()
        monitoring_layout = QHBoxLayout(monitoring_tab)
        monitoring_layout.addWidget(self.process_management_widget)
        monitoring_layout.addWidget(self.cpu_chart_widget)
        tab_widget.addTab(monitoring_tab, "Monitoring")

        # Create Database tab
        database_tab = QWidget()
        database_layout = QVBoxLayout(database_tab)
        database_layout.addWidget(self.database_widget)
        tab_widget.addTab(database_tab, "Database")

        self.setCentralWidget(tab_widget)

        self.cpu_watcher.new_data.connect(self.cpu_chart_widget.update_chart)
        self.cpu_watcher.insert_record.connect(self.database_widget.insert_cpu_workload)
        self.cpu_watcher.stopped.connect(self.thread_stopped)

        self.create_menu()

    def create_default(self):
        """
        Create default settings
        """
        if not os.path.isdir(os.path.join(appdata_local_path(), 'cpu-usage-monitor')):
            os.makedirs(os.path.join(appdata_local_path(), 'cpu-usage-monitor'))

        if not os.path.isfile(self.settings_file):
            with open(self.settings_file, 'w') as file:
                print(f'Created settings file: {self.settings_file} with default settings')
                json.dump(DEFAULT_SETTINGS, file)

    def load_settings(self):
        print('MainWindows.load_settings()')
        self.create_default()
        with open(self.settings_file, 'r') as file:
            self.settings = json.load(file)
            print(f'Init with settings: {self.settings}')

    def create_menu(self):
        menubar = self.menuBar()

        # Monitoring menu
        monitoring_menu = menubar.addMenu("Monitoring")
        start_action = QAction("Start", self)
        stop_action = QAction("Stop", self)
        monitoring_menu.addAction(start_action)
        monitoring_menu.addAction(stop_action)

        # Database menu
        database_menu = menubar.addMenu("Data")
        export_action = QAction("Export...", self)
        import_action = QAction("Import...", self)
        settings_action = QAction("Settings...", self)
        database_menu.addAction(export_action)
        database_menu.addAction(import_action)

        # noinspection PyUnresolvedReferences
        settings_action.triggered.connect(self.show_settings)
        database_menu.addAction(settings_action)

        # About menu
        help_menu = menubar.addMenu("Help")
        docs_action = QAction("Help", self)
        about_action = QAction("About", self)
        help_menu.addAction(docs_action)
        help_menu.addAction(about_action)

    def closeEvent(self, event):
        """
        Stop the CPU watcher thread when the window is closed
        :param event: QCloseEvent
        """
        self.cpu_watcher.stop()
        event.accept()

    def thread_stopped(self):
        """
        Close the window when the CPU watcher thread is stopped
        """
        self.close()

    def show_settings(self):
        """
        Show settings window
        """
        settings_widget = SettingsWidget(settings_file=self.settings_file, parent=self)
        print(f'Showing settings window with settings: {self.settings}')
        if settings_widget.exec_():
            self.load_settings()


def main():
    """
    Main function, create the application and main window
    Catches Ctrl-C and gracefully stop the CPU watcher thread
    :return: `sys.exit` return code
    """
    app = QApplication(sys.argv)
    cpu_watcher = CPUWatcher([], interval=1)
    window = MainWindow(cpu_watcher)
    window.show()

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        # We are here after Ctrl-C
        cpu_watcher.stop()
        window.process_management_widget.cpu_watcher_thread.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())
