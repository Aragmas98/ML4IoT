from sqlite3 import Timestamp
from DoSomething import DoSomething 
import time
import json 
from datetime import datetime 


if __name__ == '__main__':
    publisher = DoSomething('publisher 1')
    publisher.run()

    while True:
        # GET DATE AND TIME 
        now = datetime.now()
        timestamp = str((now.timestamp()))
        # PACK INFO INTO A JSON
        timestamp_json = json.dumps({'timestamp':timestamp})
        # SEND INFO THROUGH MQTT
        publisher.myMqttClient.myPublish('/4jb8hs4/timestamp', timestamp_json)

        time.sleep(5)