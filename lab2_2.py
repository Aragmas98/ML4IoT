import tensorflow as tf 
import time
import os

L = 1000 #ms = 1sec
l = 40 #ms
s = 20 #ms

frame_length = 16*l # 16 [samples/ms] * 40 [ms]
frame_step = 16*s

filename1 = './outputs/l2_2_audio16.wav'
filename2 = './outputs/l2_2_tensor.txt'
filename3 = './outputs/l2_2_tensor.png'

#Read the audio signal
audio = tf.io.read_file(filename1)

#Convert the signal in a TensorFlow
tf_audio, rate = tf.audio.decode_wav(audio)
tf_audio = tf.squeeze(tf_audio, 1)


# Convert the waveform in a spectrogram applying the STFT
print('...stft...')
start = time.time()
stft = tf.signal.stft(tf_audio, 
 frame_length=frame_length, 
 frame_step=frame_step,
 fft_length=frame_length)
spectrogram = tf.abs(stft)
end = time.time()
print(f'----[{end-start}]----')

#Convert the tensor in a byte string
tensor_bstr = tf.io.serialize_tensor(spectrogram)

#Store the string on disk
tf.io.write_file(filename2, tensor_bstr)

#Measure the size of the output file
print('original: ', os.path.getsize(filename1),' bytes')
print('spectogram: ', os.path.getsize(filename2),' bytes')


#Transpose the spectrogram to represent time on x-axis
image = tf.transpose(spectrogram)

# Add the “channel” dimension
image = tf.expand_dims(image, -1)

#Take the logarithm of the spectrogram
image = tf.math.log(image + 1.e-6)

#Apply min/max normalization
min_ = tf.reduce_min(image)
max_ = tf.reduce_max(image)
image = (image - min_) / (max_ - min_)
image = image * 255

#Cast the tensor to uint8
image = tf.cast(image, tf.uint8)

#Convert the tensor to a PNG
image = tf.io.encode_png(image)

#Store the PNG on disk
tf.io.write_file(filename3, image)