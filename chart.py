import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
from typing import List
from dataclasses import dataclass
import time
@dataclass
class PriceData():
    timestamp: List[datetime]
    smart_entry_high: List[float|None]
    smart_entry_low: List[float|None]
    price: List[float]

    def append(self, ts:datetime, high:float|None, low:float|None, price:float) -> None:
        self.timestamp.append(ts)
        self.smart_entry_high.append(high)
        self.smart_entry_low.append(low)
        self.price.append(price)

class LiveChart:

    def __init__(self, data:PriceData, n_lines=3, title="Live Chart", xlabel="X", ylabel="Y"):
        self.data: PriceData = data
        self.delta_time = time.time()
        plt.ion()  # enable interactive mode
        self.fig, self.ax = plt.subplots()
        self.lines = [self.ax.plot([], [], lw=2, label=i)[0] for i in ["smart_money_high", "smart_money_low", "price"]]
        
        date_format = DateFormatter('%H:%M:%S')
        self.ax.xaxis.set_major_formatter(date_format)
        
        plt.gcf().autofmt_xdate()
        
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.legend()
        self.started = False

    def start(self, data:PriceData):
        """Initialize and display the chart."""
        y_list = [data.smart_entry_high, data.smart_entry_low, data.price]

        for line, y_data in zip(self.lines, y_list):
            line.set_data(data.timestamp, y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        plt.show(block=False)
        self.started = True

    def update(self, pause_time=0.01):
        """
        Updates the chart with new data for all lines.\n\n
        """
        y_list = [self.data.smart_entry_high, self.data.smart_entry_low, self.data.price]
        if not self.started:
            self.start(self.data)
            return


        for line, y_data in zip(self.lines, y_list):
            line.set_data(self.data.timestamp, y_data)
        if time.time() - self.delta_time > 10:
            plt.show(block=False)
            self.delta_time = time.time()
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(pause_time)
    
    def chart_pause(self, pause_time=0.01):
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(pause_time)
