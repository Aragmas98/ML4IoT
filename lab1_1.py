from board import D4
import adafruit_dht
import time as time

import sys

dht_device = adafruit_dht.DHT11(D4)
file_path = './outputs/l1_1_measurements.txt'

original_stdout = sys.stdout # Save a reference to the original standard output
with open(file_path, 'w') as f:

    while True:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%m/%d/%Y %H:%M:%S", named_tuple)

        sys.stdout = f # Change the standard output to the file we created.
        print(time_string,temperature,humidity)
    
        time.sleep(1)

    sys.stdout = original_stdout # Reset the standard output to its original value