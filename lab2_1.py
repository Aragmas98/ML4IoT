import pyaudio
import wave
from scipy.io import wavfile
from scipy import signal
import os
import numpy as np

sample_format = pyaudio.paInt16 #16-bit resolution
chans = 1 #1 channel
samp_rate_1 = 48000 # sampling rate
samp_rate_2 = 16000
chunk = 4096 #2^12 samples for buffer
record_secs = 1 #seconds to record
dev_index = 2# index of mic_device according (p.get_device_info_by_index(i).get('name'))
wav_filename_1 = './outputs/l2_2_audio48.wav' #name of .wav file
wav_filename_2 = './outputs/l2_2_audio16.wav'

def record_audio():
    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = sample_format,rate = samp_rate_1,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("...recording...")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate_1/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("...finished recording...")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_filename_1,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(sample_format))
    wavefile.setframerate(samp_rate_1)
    wavefile.writeframes(b''.join(frames))

    wavefile.close()

def process_audio():
    #read audio signal
    rate, audio = wavfile.read(wav_filename_1)

    #resample the signal
    audio = signal.resample_poly(audio, 1, 3) # audio, up, down -> new_sp = (up/down)*old_sp

    #casting the signal to original datatype
    audio = audio.astype(np.int16)

    #storing audio
    wavfile.write(wav_filename_2, samp_rate_2, audio)


if __name__ == '__main__':
    record_audio()
    process_audio()
    print('audio48: ', os.path.getsize(wav_filename_1))
    print('audio16: ', os.path.getsize(wav_filename_2))
