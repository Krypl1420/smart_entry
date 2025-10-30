import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
class LiveChart:

    def __init__(self, n_lines=3, title="Live Chart", xlabel="X", ylabel="Y"):
        self.x_data = []
        self.y_data_list = [[] for _ in range(n_lines)]
        plt.ion()  # enable interactive mode
        self.fig, self.ax = plt.subplots()
        self.lines = [self.ax.plot([], [], lw=2, label=i)[0] for i in ["smart_money_high", "smart_money_low", "price"]]
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.legend()
        self.started = False

    def start(self, x_data, y_data_list):
        """Initialize and display the chart."""
        self.x_data.append(x_data)
        self.y_data_list.append(y_data_list)
        for line, y_data in zip(self.lines, y_data_list):
            line.set_data(x_data, y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        plt.show(block=False)
        self.started = True

    def manage_data(self, max_points=100):
        """Keep only the latest max_points data."""
        if len(self.x_data) != len(self.y_data_list[0]):
            raise ValueError("X and Y data length mismatch.")
        if len(self.x_data) > max_points:
            self.x_data.pop(0)
            for i in range(len(self.y_data_list)):
                self.y_data_list[i].pop(0)

    def update(self, x_data: datetime, y_data_list: List[int], pause_time=0.01):
        """
        Updates the chart with new data for all lines.\n\n
        Y VALUE ORDER: ["smart_money_high", "smart_money_low", "price"]
        """
        if not self.started:
            self.start(x_data, y_data_list)
            return

        for line, y_data in zip(self.lines, y_data_list):
            line.set_data(x_data, y_data)

        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(pause_time)