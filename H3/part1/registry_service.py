import cherrypy 
import json 
import base64
import os
import tensorflow as tf
import numpy as np
from DoSomething import DoSomething 
from datetime import datetime 
import time

from board import D4 
import adafruit_dht 

class RegistryService(object):

    exposed = True 
    
    def GET(self, *path, **query):
        
        operation = path[0]

        if operation == 'list':
            models = os.listdir('./models/')

            body = {
                'list' : models,
            }
            body = json.dumps(body)
            return body

        elif operation == 'predict':

            model_name = str(query.get('model'))
            print(model_name)
            if model_name is None:
                raise cherrypy.HTTPError(400, 'WRONG QUERY - model')
            
            tthres = float(query.get('tthres'))
            print(tthres, type(tthres))
            if tthres is None:
                raise cherrypy.HTTPError(400, 'WRONG QUERY - tthres')
            
            hthres = float(query.get('hthres'))
            print(hthres, type(hthres))
            if hthres is None:
                raise cherrypy.HTTPError(400, 'WRONG QUERY - hthres')

            print('model read correctly')

            dht_device = adafruit_dht.DHT11(D4)

            print('dht device created')

            model_path = f"./models/{model_name}"
            
            tensor_specs = (tf.TensorSpec([None, 6, 2], dtype=tf.float32), tf.TensorSpec([None, 1, 2]))
            interpreter = tf.lite.Interpreter(model_path=model_path)
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            interpreter.allocate_tensors()

            print('interpreter allocated')


            mean = np.array([ 9.107597, 75.904076])
            std = np.array([ 8.654227, 16.557089])

            data = []

            for i in range(1,20):
                
                temperature = dht_device.temperature 
                humidity = dht_device.humidity

                if i%7 != 0:
                    #read a value and append
                    data.append([temperature, humidity])
                    print('value added')
                    
                else:
                    #do prediction and restart.
                    print('prediction started')
                    x = np.array(data)
                    y_true = np.array([temperature, humidity])

                    x = (x - mean) / (std + 1.e-6)
                    x = tf.convert_to_tensor(x, dtype=tf.float32)
                    x = tf.expand_dims(x, 0)

                    print('data prepared')
                    interpreter.set_tensor(input_details[0]['index'], x)
                    interpreter.invoke()
                    y_pred = interpreter.get_tensor(output_details[0]['index'])
                    print('prediction done')
                    mae = np.mean(np.abs(y_pred - y_true), axis=1)
                    
                    data = []
                    
                    print(mae, mae.shape)
                    print(y_pred, y_pred.shape)
                    
                    if mae[0][0] > tthres:
                        print('publishing tthres...')
                        now = datetime.now()
                        timestamp = int(now.timestamp())
                        body = {
                            "bn":"raspberrypi.local",
                            "bt": timestamp, 
                            "e": [
                                {"n":"Temperature", "u":"Cel", "t":0, "v":float(y_true[0])},
                                {"n":"Prediction", "u":"Cel", "t":0, "v":float(y_pred[0][0][0])},
                            ]
                        }
                        body = json.dumps(body)
                        publisher.myMqttClient.myPublish('/ML4IoT/Group17/H3/e1/alert', body)
                        

                    if mae[0][1] > hthres:
                        print('publishing hthres...')
                        now = datetime.now()
                        timestamp = int(now.timestamp())
                        body = {
                            "bn":"raspberrypi.local",
                            "bt": timestamp, 
                            "e": [
                                {"n":"Humidity", "u":"%", "t":0, "v":float(y_true[1])},
                                {"n":"Prediction", "u":"%", "t":0, "v":float(y_pred[0][0][1])},
                            ]
                        }
                        body = json.dumps(body)
                        publisher.myMqttClient.myPublish('/ML4IoT/Group17/H3/e1/alert', body)

                time.sleep(1)

            
    def POST(self, *path, **query):
        pass

    def PUT(self, *path, **query):
        
        operation = path[0]

        if operation == 'add':

            body_str = cherrypy.request.body.read()

            body = json.loads(body_str)
            if body is None:
                raise cherrypy.HTTPError(400, 'MISSING BODY ERROR - BODY')    
            
            model_b64str = body['model']
            if model_b64str is None:
                raise cherrypy.HTTPError(400, 'MISSING BODY ERROR - MODEL')

            name = body['name']
            if name is None:
                raise cherrypy.HTTPError(400, 'MISSING BODY ERROR - NAME')

            model_b64 = model_b64str.encode()
            model = base64.urlsafe_b64decode(model_b64)

            models_path = './models/'
            if not os.path.exists(models_path):
                os.makedirs(models_path)

            with open(f"{models_path}/{name}", "wb") as outfile:
                outfile.write(model)


    def DELETE(self, *path, **query):
        pass


if __name__ == '__main__':

    publisher = DoSomething('publisher 1')
    publisher.run()

    conf = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.tree.mount(RegistryService(), '', conf) 
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port':8080})
    cherrypy.engine.start() 
    cherrypy.engine.block()