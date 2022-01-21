from datetime import datetime
from DoSomething import DoSomething 
import json
import time

# class Subscriber(DoSomething):
#     def notify(self, topic, msg):
#         #what to do after the client receives the message
#         print('>>>> ' ,topic)
        # input_json = json.loads(msg)
        # timestamp = input_json['timestamp']
        # now = datetime.fromtimestamp(float(timestamp))
        # datetime_str = now.strftime('%d-%m-%y %H:%M:%S')
        # print(topic, datetime_str)


if __name__ == '__main__':
    subscriver = DoSomething('subscriber 1')
    subscriver.run() 
    subscriver.myMqttClient.mySubscribe('/4jb8hs4/timestamp')
    print('subscription done successfully!')

    while True:
        time.sleep(1)