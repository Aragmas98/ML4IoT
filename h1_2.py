import os
import sys
import zipfile
import tensorflow as tf


file_path = './inputs/H1_yes_no/' #path to unziped files

L = 1000 #ms
l = 40 #ms
s = 20 #ms

rate = 16 #[samples/ms]

frame_length = 16*l # 16 [samples/ms] * 40 [ms]
frame_step = 16*s


num_mel_bins = 40
sampling_rate = 16000
lower_frequency = 20 #Hz
upper_frequency = 4000 #Hz

coefs = 10


for filename in os.listdir(file_path):
    if not os.path.isdir(filename):
        
        #Read the audio signal
        audio = tf.io.read_file(f'{file_path}{filename}')
        
        #Convert the signal in a TensorFlow
        tf_audio, rate = tf.audio.decode_wav(audio)
        tf_audio = tf.squeeze(tf_audio, 1)

        # Convert the waveform in a spectrogram applying the STFT
        stft = tf.signal.stft(tf_audio, 
                    frame_length=frame_length, 
                    frame_step=frame_step,
                    fft_length=frame_length)
        spectrogram = tf.abs(stft)

        #Compute the log-scaled Mel spectrogram
        num_spectrogram_bins = spectrogram.shape[-1]

        linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
                    num_mel_bins,
                    num_spectrogram_bins,
                    sampling_rate,
                    lower_frequency,
                    upper_frequency)

        mel_spectrogram = tf.tensordot(
                    spectrogram, 
                    linear_to_mel_weight_matrix,
                    1)
        
        log_mel_spectrogram = tf.math.log(mel_spectrogram + 1e-6)

        #Compute the MFCCs
        mfccs = tf.signal.mfccs_from_log_mel_spectrograms(
                    log_mel_spectrogram)[...,:coefs]
