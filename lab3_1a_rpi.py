import argparse 
import numpy as np
import tensorflow as tf 
import time 


parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
args = parser.parse_args() 


interpreter = tf.lite.Interpreter(model_path='./models/{}.tflite'.format(args.model))
interpreter.allocate_tensors() 


input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details() 

input_shape = input_details[0]['shape']


times = []

for i in range(100):
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    start = time.time()
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    end = time.time()
    times.append(end-start)

print('{:.3f}ms'.format(np.mean(times)*1000.))