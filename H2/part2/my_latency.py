#To run on board
import argparse
import numpy as np
from subprocess import call
import tensorflow as tf
import time
from scipy import signal

import zlib
import os

print('hello')

model_path = './model.tflite'

with open(model_path, 'rb') as fp:
    decomp_model = zlib.decompress(fp.read())
    decomp_model_path = model_path[:-4] # .tf file
    
    file = open(decomp_model_path,'wb')
    file.write(decomp_model)
    file.close()

print('Compressed-File size: ' + str(round(os.path.getsize(model_path)/1024, 4)) + ' Kilobytes')
print('Decompressed-File size: ' + str(round(os.path.getsize(decomp_model_path)/1024, 4)) + ' Kilobytes')

#Evaluation
model = decomp_model_path#'DSCNN.tflite' #path tflite
rate = 16000
mfcc = True
if(mfcc):
  length = 256
  stride = 128
else:
  length = 256
  stride = 128
resize = 32
num_mel_bins = 40
num_coefficients = 10

num_frames = (rate - length) // stride + 1
num_spectrogram_bins = length // 2 + 1

linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins, num_spectrogram_bins, rate, 20, 4000)

if model is not None: 
    interpreter = tf.lite.Interpreter(model_path=model)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

inf_latency = []
tot_latency = []
for i in range(100):
    sample = np.array(np.random.random_sample(48000), dtype=np.float32)

    start = time.time()

    # Resampling
    sample = signal.resample_poly(sample, 1, 48000 // rate)

    sample = tf.convert_to_tensor(sample, dtype=tf.float32)

    # STFT
    stft = tf.signal.stft(sample, length, stride,
            fft_length=length)
    spectrogram = tf.abs(stft)

    if mfcc is False and resize > 0:
        # Resize (optional)
        spectrogram = tf.reshape(spectrogram, [1, num_frames, num_spectrogram_bins, 1])
        spectrogram = tf.image.resize(spectrogram, [resize, resize])
        input_tensor = spectrogram
    else:
        # MFCC (optional)
        mel_spectrogram = tf.tensordot(spectrogram, linear_to_mel_weight_matrix, 1)
        log_mel_spectrogram = tf.math.log(mel_spectrogram + 1.e-6)
        mfccs = tf.signal.mfccs_from_log_mel_spectrograms(log_mel_spectrogram)
        mfccs = mfccs[..., :num_coefficients]
        mfccs = tf.reshape(mfccs, [1, num_frames, num_coefficients, 1])
        input_tensor = mfccs

    if model is not None:
        interpreter.set_tensor(input_details[0]['index'], input_tensor)
        start_inf = time.time()
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

    end = time.time()
    tot_latency.append(end - start)

    if model is None:
        start_inf = end

    inf_latency.append(end - start_inf)
    time.sleep(0.1)

print('Inference Latency {:.2f}ms'.format(np.mean(inf_latency)*1000.))
print('Total Latency {:.2f}ms'.format(np.mean(tot_latency)*1000.))