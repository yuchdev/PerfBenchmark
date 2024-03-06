import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from cpu_monitor import CPUWatcher
from process_management_widget import ProcessManagementWidget
from cpu_chart_widget import CPUChartWidget


class MainWindow(QMainWindow):
    def __init__(self, cpu_watcher):
        super().__init__()
        self.setWindowTitle("CPU Usage Monitor")
        self.setGeometry(20, 20, 1000, 600)

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
        self.cpu_watcher.stop()
        event.accept()

    def thread_stopped(self):
        self.close()



def main():
    app = QApplication(sys.argv)
    cpu_watcher = CPUWatcher([], interval=1)  # Empty list of processes initially

    window = MainWindow(cpu_watcher)
    window.show()

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        cpu_watcher.stop()
        window.process_management_widget.cpu_watcher_thread.join()


if __name__ == "__main__":
    main()
