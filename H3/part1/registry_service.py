import cherrypy 
import json 
import base64
import os
import tensorflow as tf
import numpy as np
from DoSomething import DoSomething 
from datetime import datetime 

data = [[14.1 , 95.8 ],
            [13.97, 96.1 ],
            [13.75, 96.3 ],
            [13.7 , 96.8 ],
            [13.83, 97.2 ],
            [13.82, 97.4 ],
            [13.73, 97.8 ],
            [13.68, 98.  ],
            [13.55, 98.3 ],
            [13.53, 98.5 ],
            [13.53, 98.6 ],
            [13.5 , 98.7 ],
            [13.46, 98.8 ],
            [13.46, 98.8 ],
            [13.43, 98.9 ],
            [13.45, 98.9 ],
            [13.33, 98.9 ],
            [13.26, 99.  ],
            [13.28, 99.1 ],
            [13.25, 99.1 ]]

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
                raise cherrypy.HTTPError(400, 'WRONG QUERY - MODEL')

            model_path = f"./models/{model_name}"

            tensor_specs = (tf.TensorSpec([None, 6, 2], dtype=tf.float32), tf.TensorSpec([None, 1, 2]))
            interpreter = tf.lite.Interpreter(model_path=model_path)
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            interpreter.allocate_tensors()

            mean = np.array([ 9.107597, 75.904076])
            std = np.array([ 8.654227, 16.557089])

            x = data[:6]
            y_true = data[6]

            x = (x - mean) / (std + 1.e-6)
            x = tf.convert_to_tensor(x, dtype=tf.float32)
            x = tf.expand_dims(x, 0)
            
            interpreter.set_tensor(input_details[0]['index'], x)
            interpreter.invoke()
            y_pred = interpreter.get_tensor(output_details[0]['index'])

            mae = np.mean(np.abs(y_pred - y_true), axis=1)
            
            now = datetime.now()
            timestamp = str((now.timestamp()))
            # PACK INFO INTO A JSON
            timestamp_json = json.dumps({'timestamp':timestamp})
            # SEND INFO THROUGH MQTT
            print('publishing...')
            publisher.myMqttClient.myPublish('/4jb8hs4/timestamp', timestamp_json)
            

            


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