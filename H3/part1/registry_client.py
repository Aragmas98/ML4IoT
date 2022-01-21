import base64 
import requests
import json

from datetime import datetime
from DoSomething import DoSomething 
import json
import time


class Subscriber(DoSomething):
    def notify(self, topic, msg):
        
        msg_json = json.loads(msg)
        timestamp = int(msg_json['bt'])
        time_str = datetime.fromtimestamp(timestamp).isoformat()
        for e in msg_json['e']:
            print(f"{time_str} {e['n']}: {e['v']}")



if __name__ == '__main__':
    subscriver = Subscriber('subscriber 1')
    subscriver.run() 
    subscriver.myMqttClient.mySubscribe('/ML4IoT/Group17/H3/e1/alert')
    
    url = "http://localhost:8080/predict?model=model_1.tf&tthres=0.1&hthres=0.1"

    r = requests.get(url)
    print(r.status_code)

    while True:
        time.sleep(1)

    
# ======================================================================

# url = f"http://localhost:8080/list"

# r = requests.get(url)
# print(r.status_code)

# r = r.json()

# for model in r['list']:
#     print(model)
    
# ======================================================================

# def get_base64_encoded_model(model_path):
#     with open(model_path, "rb") as model_file:
#         return base64.urlsafe_b64encode(model_file.read()).decode()

# model_path = './model.tflite'
# model_b64str = get_base64_encoded_model(model_path)

# name = 'modelA.tflite'

# body = {
#     'name': name, 
#     'model': model_b64str
# }
# body = json.dumps(body)

# url = f"http://localhost:8080/add"

# r = requests.put(url,data=body)
# print(r.status_code)
