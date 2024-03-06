import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from process_management_widget import ProcessManagementWidget
from cpu_chart_widget import CPUChartWidget
from cpu_monitor import CPUWatcher


# noinspection PyPep8Naming
class MainWindow(QMainWindow):
    """
    Application main window
    Assume width 90% of screen width and height 80% of screen height
    """

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
        self.setGeometry(20, 20, screen_width * 0.9, screen_height * 0.8)

        # Widgets
        self.cpu_watcher = cpu_watcher
        self.cpu_chart_widget = CPUChartWidget(self)
        self.process_management_widget = ProcessManagementWidget(cpu_watcher)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.process_management_widget)
        main_layout.addWidget(self.cpu_chart_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.cpu_watcher.new_data.connect(self.cpu_chart_widget.update_chart)
        self.cpu_watcher.stopped.connect(self.thread_stopped)

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
