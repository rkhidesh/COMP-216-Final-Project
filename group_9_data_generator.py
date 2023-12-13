import random
import math
import json
import time
from datetime import datetime


# Class for generating temperature data
class TemperatureGenerator:
    #  code is taken from our lab 6
    def __init__(self):
        self.__angle = 0
        self.__delta = 0.017 / (24 * 6)  # Every 10 mins = 24 h a day with 12 compositions of 10 mins in an hour
        self.__temperature = 15
        self.__shift = -math.pi / 2  # Shift so winter is cold
        self.__daily_variation = 0.1  # Daily temperature variation
        self.__noise_factor = 0.2  # Adjust the noise factor for realistic changes
        self.__temperature_data = []

    # private method to generate a temperate value
    def __sin(self):
        sin_value = self.__temperature * math.sin(self.__angle + self.__shift)
        return sin_value

    @property
    def generate_data(self):
        daily_variation = random.uniform(-self.__daily_variation, self.__daily_variation)
        noise = random.uniform(-self.__noise_factor, self.__noise_factor)
        sin_value = self.__sin() + daily_variation + noise
        self.__angle += self.__delta

        # # Add current value to the temperature_data
        self.__temperature_data.append(sin_value)

        return self.__temperature_data

    def package_data(self, num_sample):
        data_package = []

        for i in range(num_sample):
            time_stamp = time.asctime()  # Getting the current timestamp
            packet_id = i + 1  # Packet IDs starting from 1
            value = self.generate_data  # Generating a temperature value
            data_package.append({
                "Time Stamp": time_stamp,
                "Packet Id": packet_id,
                "Temperature Value": value
            })

        return json.dumps(data_package)  # Return the generated data list
