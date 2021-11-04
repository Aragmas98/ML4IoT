import argparse
from board import D4
import adafruit_dht
import time as time


parser = argparse.ArgumentParser()
parser.add_argument('--filename', type=str, help='output file name', required=True)
args = parser.parse_args()


dht_device = adafruit_dht.DHT11(D4)

with open(args.filename, 'w') as f:

    while True:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        time_now = time.localtime()
        time_string = time.strftime("%d/%m/%Y,%H:%M:%S", time_now)

        f.write(f'{time_string},{temperature},{humidity}\n')

        time.sleep(1)