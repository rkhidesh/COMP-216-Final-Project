import threading
import tkinter as tk
import random
import time
import group_9_data_generator
from group_9_subscriber import *
from group_9_data_generator import *
import paho.mqtt.client as mqtt


class Publisher:

    def __init__(self, root):
        self.temperature_generator = TemperatureGenerator()
        self.topic = "Temperature Sensor"  # Default topic
        self.init_variables()

        # Setting up the window for GUI
        self.root = root
        self.root.title("COMP216 - Final Project")
        self.root.geometry(f"{400}x{500}")  # Set window size
        self.root.configure(bg='#DDFFBB')  # You can adjust the color code

        # Create GUI elements
        self.create_gui()

    def init_variables(self):
        self.now = datetime.now()
        self.stored_time = None
        self.is_publishing = False
        self.packet_id = 1  # the initial packet ID
        self.current_time = self.now.strftime("%B %d, %Y %H:%M:%S")
        # Creating a thread to constantly update current time
        self.time_thread = threading.Thread(target=self.update_current_time_thread)
        self.time_thread.daemon = True
        self.time_thread.start()

    def set_topic_entry(self, entry_widget):
        # Get the topic from the entry widget
        self.topic = entry_widget.get()
        print(f"Topic set to: {self.topic}")

    # Creating the GUI elements
    def create_gui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#DDFFBB")  # Light green background
        header_frame.pack(side=tk.TOP, fill=tk.X)

        college_label = tk.Label(header_frame, text="Centennial College", bg="#DDFFBB", font=("Arial", 14, "bold"))
        college_label.pack(pady=5)

        course_label = tk.Label(header_frame, text="COMP 216 - 402", bg="#DDFFBB", font=("Arial", 11, "bold"))
        course_label.pack(pady=5)

        separator = ttk.Separator(root, orient='horizontal')
        separator.pack(fill='x')

        # Topic
        topic_frame = self.create_label_frame("Topic: ")
        self.topic_text = self.create_label(topic_frame)

        # Entry widget for user input
        topic_entry = tk.Entry(topic_frame)
        topic_entry.insert(0, "Temperature Sensor")
        topic_entry.pack(side=tk.LEFT, padx=10)

        # Set Topic button
        set_topic_button = tk.Button(topic_frame, text="Set Topic", command=lambda: self.set_topic_entry(topic_entry))
        set_topic_button.pack(side=tk.LEFT, padx=10)

        # Last Update
        last_update_frame = self.create_label_frame("Last Update:")
        self.last_update_text = self.create_label(last_update_frame)

        # Interval
        interval_frame = self.create_label_frame("Interval Since Last Update:")
        self.interval_text = self.create_label(interval_frame)

        # Current time
        current_time_frame = self.create_label_frame("Current Time:")
        self.current_time_text = self.create_label(current_time_frame)

        # Output label
        output_label = tk.Label(self.root, text="Data Received:", bg="#DDFFBB")
        output_label.pack(side=tk.TOP, pady=10)

        self.text_box = tk.Text(root, width=40, height=10)
        self.text_box.pack(side=tk.TOP, padx=10)

        # Button frame
        button_frame = tk.Frame(self.root, bg="#DDFFBB")
        button_frame.pack(side=tk.TOP, pady=10)

        # Start button
        start_button = tk.Button(button_frame, text="Start Publishing", command=self.start_publishing)
        start_button.pack(side=tk.LEFT, padx=10)

        # Stop button
        stop_button = tk.Button(button_frame, text="Stop Publishing", command=self.stop_publishing)
        stop_button.pack(side=tk.LEFT, padx=10)

    # Displaying the labels in the window
    def create_label_frame(self, label_text):
        frame = tk.Frame(self.root, bg="#DDFFBB")
        frame.pack(side=tk.TOP, padx=10, pady=5, fill=tk.X)
        label = tk.Label(frame, text=label_text, bg="#DDFFBB")
        label.pack(side=tk.LEFT)
        return frame

    def create_label(self, parent, text=""):
        label = tk.Label(parent, text=text, bg="#DDFFBB")
        label.pack(side=tk.LEFT)
        return label

    # This function is called when the Start Publishing button is pressed
    def start_publishing(self):
        def display_data():
            if not self.is_publishing:
                return

            num_samples = 1
            data_package = json.loads(TemperatureGenerator().package_data(num_samples))[0]

            # Update the Packet ID sequentially
            data_package['Packet Id'] = self.packet_id
            self.packet_id += 1

            display_text = f"\nTime Stamp: {data_package['Time Stamp']}\n" \
                           f"Packet ID: {data_package['Packet Id']}\n" \
                           f"Temperature Value: {data_package['Temperature Value']}\n" \
                           f"Topic set to: {self.topic}"

            self.text_box.config(state="normal")  # Enable the text box for editing
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, display_text)
            self.text_box.config(state="disabled")  # Disable the text box for editing

            current_time = datetime.now()

            formatted_time = current_time.strftime('%B %d, %Y %H:%M:%S')
            self.current_time_text.config(text=formatted_time)

            # Calculate and update the interval since the last update
            if self.stored_time is not None:
                interval = current_time - self.stored_time
                self.interval_text.config(text=f"{interval}")
                # Update the "Last Update" label
                self.last_update_text.config(text=f"{current_time.strftime('%B %d, %Y %H:%M:%S')}")

            if not hasattr(self, 'initial_stored_time'):
                self.initial_stored_time = current_time
            self.stored_time = current_time

            if self.is_publishing:
                self.display_data_job = self.root.after(1000, display_data)

        # If there's a scheduled update, cancel it before scheduling a new one
        if hasattr(self, 'display_data_job'):
            self.root.after_cancel(self.display_data_job)

        self.is_publishing = True
        display_data()

    def stop_publishing(self):
        self.is_publishing = False
        self.text_box.delete(1.0, tk.END)

        self.update_current_time()

    def update_current_time_thread(self):
        while True:
            self.root.after(1000, self.update_current_time)
            time.sleep(1)

    def update_current_time(self):
        while True:
            current_time = datetime.now()
            formatted_time = current_time.strftime('%B %d, %Y %H:%M:%S')
            self.current_time_text.config(text=f"{formatted_time}")
            self.root.update()  # Update the GUI
            time.sleep(1)

    # Sending data to broker
    def send_data(self, broker='localhost', port=1883, topic='weather_topic', num_samples=500, ):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.num_samples = num_samples
        client = mqtt.Client()
        client.connect(self.broker, self.port)
        while True:
            try:
                self.data = self.temperature_generator.package_data(self.num_samples)
                client.publish(self.topic, self.data)
                print('Connected to the server!')
                time.sleep(1)
            except Exception as e:
                print(f"Error sending data: {e}")
                time.sleep(1)


if __name__ == "__main__":
    root = tk.Tk()
    publisher = Publisher(root)
    root.mainloop()
