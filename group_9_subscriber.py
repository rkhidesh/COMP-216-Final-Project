import threading
import json
import tkinter as tk
from datetime import datetime, time
from tkinter import ttk
from group_9_publisher import *
import paho.mqtt.client as mqtt

# Import the TemperatureGenerator class from the data generator file
from group_9_data_generator import TemperatureGenerator


class Subscriber:
    def __init__(self, root, topic="Temperature Sensor"):
        # Setting up MQTT
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.topic = topic
        self.root = root
        self.root.title("Subscriber GUI")

        self.canvas_width = 600
        self.canvas_height = 300
        # Initialize an instance of the TemperatureGenerator
        self.temperature_generator = TemperatureGenerator()

        self.line = False

        self.init_ui()

    def subscribe(self):
        # Calling the topic from Publisher class
        topic = self.topic
        topic = self.publisher.topic

        # Subscribing to the topic
        self.client.subscribe(topic)
        self.client.connect("localhost", 1883, 60)
        self.client.loop_forever()

    def on_message(self, client, userdata, message):
        # Decode the message payload
        data = message.payload.decode("utf-8")

        if self.out_of_range(data):
            print("Warning, out of range data detected!")

        # Detecting and handling missing data
        if not data:
            print("Warning, data is missing!")

        # Convert the decoded string to a dict using json.loads()
        data_package_dict = json.loads(data)

    def out_of_range(self, data):
        try:
            value = float(json.loads(data)["Temperature Value"])
            # Defining our acceptable range based on our data generator
            min_value, max_value = -18, 34

            if not min_value <= value <= max_value:
                return True  # Out of range
        except (json.JSONDecodeError, KeyError, ValueError):
            return True  # Data missing

        return False  # Within the acceptable range

    def init_ui(self):
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack()

        # Calling the draw_chart method
        self.btn_display = tk.Button(self.input_frame, text="Go", command=self.draw_chart, width=10)
        self.btn_display.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="#DDFFBB")
        self.canvas.pack()

        # Create a label of Temperature
        self.temperature_label = tk.Label(self.root, text="Temperature ", bg="#DDFFBB", font=("Calibri", 12))
        self.temperature_label.place(x=40, y=40)

        # Create a scrollbar for when more values occur
        self.scrollbar = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a thread and set the target to the method in step 1
        # Set the daemon property of the above thread to True.
        thread = threading.Thread(target=self.extra_method, daemon=True)

        # Start the thread
        thread.start()

    def draw_chart(self):
        self.line = True
        # Get the most recent temperature values from the data generator
        num_samples = 1
        data_package = json.loads(self.temperature_generator.package_data(num_samples))[0]
        temperature_values = data_package['Temperature Value']

        # Draw the chart using the most recent temperature values
        self.draw_line(5, 5, temperature_values)

    def extra_method(self):
        # infinite loop
        while True:
            if self.line:
                # Get temperature values from the data generator
                num_samples = 2
                data_package = json.loads(self.temperature_generator.package_data(num_samples))[0]
                temperature_values = data_package['Temperature Value']

                self.draw_line(5, 5, temperature_values)

                time.sleep(0.5)

    def draw_line(self, x_spacing, x_width, y_values):
        self.canvas.delete("all")
        num_points = len(y_values)
        curve_points = []

        scaling_factor = 5
        y_min = -18
        y_max = -10

        for i in range(num_points):
            x = i * (x_spacing + x_width) + x_spacing + x_width / 2
            # Center the line vertically
            # y = self.canvas_height / 2 - (y_values[i] / 2)
            y = self.canvas_height - ((y_values[i] - y_min) / (y_max - y_min) * self.canvas_height)
            y = max(min(y, self.canvas_height), 0)
            curve_points.extend([x, y])

        self.canvas.create_line(curve_points, fill="red", width=2, smooth=True)

if __name__ == "__main__":
    root = tk.Tk()
    subscriber = Subscriber(root, topic="Temperature Sensor")
    root.mainloop()
