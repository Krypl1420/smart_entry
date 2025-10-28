import matplotlib.pyplot as plt


class LiveChart:
    def __init__(self, n_lines=3, title="Live Chart", xlabel="X", ylabel="Y"):
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
        for line, y_data in zip(self.lines, y_data_list):
            line.set_data(x_data, y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        plt.show(block=False)
        self.started = True

    def update(self, x_data, y_data_list, pause_time=0.01):
        """Update the chart with new data for all lines."""
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