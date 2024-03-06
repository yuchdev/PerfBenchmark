from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt


class CPUChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_chart = plt.figure()
        self.cpu_ax = self.cpu_chart.add_subplot(111)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cpu_chart.canvas)

    def update_chart(self, cpu_usage_history):
        self.cpu_ax.clear()
        for pid, usage in cpu_usage_history[-1].items():
            self.cpu_ax.plot(range(len(cpu_usage_history)),
                             [process_usage.get(pid, 0) for process_usage in cpu_usage_history], label=f"Process {pid}")
        self.cpu_ax.set_xlabel('Time (ticks)')
        self.cpu_ax.set_ylabel('CPU Usage (%)')
        self.cpu_ax.legend()
        self.cpu_chart.canvas.draw()
