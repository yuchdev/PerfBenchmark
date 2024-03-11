from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt


class CPUChartWidget(QWidget):
    """
    Widget to display the CPU usage chart
    Legend: x-axis: time (ticks), y-axis: CPU usage (%)
    Automatically scales charts and provide legend
    """

    def __init__(self, parent=None):
        """
        The construction subplot(111) is a shorthand notation
        for creating a subplot on a 1x1 grid at the 1st position.
        This notation is equivalent to specifying add_subplot(nrows=1, ncols=1, index=1)
        :param parent: parent widget
        """
        super().__init__(parent)
        self.cpu_chart = plt.figure()
        self.cpu_ax = self.cpu_chart.add_subplot(111)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cpu_chart.canvas)

    def update_chart(self, cpu_usage_history: list):
        """
        Accepts a list of dictionaries containing CPU usage of each process
        Usually updates with single point
        :param cpu_usage_history: list of PID and payload, e.g. [{1: 10, 2: 20}, {1: 20, 2: 30}]
        """
        self.cpu_ax.clear()
        for pid, usage_tuple in cpu_usage_history[-1].items():
            # Unpack the tuple
            usage, _ = usage_tuple
            self.cpu_ax.plot(
                range(len(cpu_usage_history)), [
                    process_usage.get(pid, 0)[0] for process_usage in cpu_usage_history
                ], label=f"Process {pid}"
            )
        self.cpu_ax.set_xlabel('Time (ticks)')
        self.cpu_ax.set_ylabel('CPU Usage (%)')
        self.cpu_ax.legend()
        self.cpu_chart.canvas.draw()
