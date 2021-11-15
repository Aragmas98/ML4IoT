import os
import sys
import zipfile
import tensorflow as tf
import time
import numpy as np
import pandas as pd

def MFCC_slow(file_path, frame_length, frame_step, num_mel_bins, sampling_rate, lower_frequency, upper_frequency, coefs):

    results = []
    
    for i, filename in enumerate(os.listdir(file_path)):
        if not os.path.isdir(filename):

            time0 = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<

            #Read the audio signal
            audio = tf.io.read_file(f'{file_path}{filename}')

            #Convert the signal in a TensorFlow
            tf_audio, rate = tf.audio.decode_wav(audio)
            tf_audio = tf.squeeze(tf_audio, 1)

            time1 = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<

            # Convert the waveform in a spectrogram applying the STFT
            stft = tf.signal.stft(tf_audio, 
                        frame_length=frame_length, 
                        frame_step=frame_step,
                        fft_length=frame_length)
            spectrogram = tf.abs(stft)

            time2 = time.time()#<<<<<<<<<<<<<<<<<<<<<<<<

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

            time3 = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<

            #Compute the MFCCs
            mfccs = tf.signal.mfccs_from_log_mel_spectrograms(
                        log_mel_spectrogram)[...,:coefs]

            time4 = time.time()
            
            duration = time4 - time0
            
            res_list = [duration, (time1 - time0), (time2 - time1), (time3 - time2), (time4 - time3)]

            results.append(res_list)

            # if i == 20:
            #     return results


    return results


def MFCC_fast(file_path, frame_length, frame_step, num_mel_bins, sampling_rate, lower_frequency, upper_frequency, coefs):
    
    times = []

    for filename in os.listdir(file_path):
        if not os.path.isdir(filename):
            pass
    
    return times


if __name__ == "__main__":
    VERSION = 1.5
    print(f'--- V.{VERSION} ---')


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

    print('|--- MFCC_slow ...')
    start_time = time.time()
    times_MFCC_slow = MFCC_slow(file_path, frame_length, frame_step, num_mel_bins, sampling_rate, lower_frequency, upper_frequency, coefs)
    end_time = time.time()
    tags = ['reading', 'sftf', 'mel', 'mfccs']
    print("|   |--- Average execution time: ", np.mean(times_MFCC_slow, axis=0)[0]*1000, ' ms')
    print("|   |      |--- tags: ", tags)
    print("|   |      |--- ms: ", np.mean(times_MFCC_slow, axis=0)[1:]*1000)
    print("|   |      |--- %: ", np.mean(times_MFCC_slow, axis=0)[1:]/np.mean(times_MFCC_slow, axis=0)[0])
    print("|   |--- Total execution time: ", (end_time-start_time)/60.0, ' min')
    print("|   |      |--- Effective min: ",  np.sum(times_MFCC_slow, axis=0)[0]/60.0)
    print("|   |      |--- Effective %: ", np.sum(times_MFCC_slow, axis=0)[0]/(end_time-start_time))
    print("|   |--- Executed files: ", len(times_MFCC_slow))
