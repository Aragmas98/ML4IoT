import tensorflow as tf 


filename1 = './outputs/l2_2_tensor.txt'
filename2 = './outputs/l2_2_MFCC.txt'
num_mel_bins = 40
sampling_rate = 16000
lower_frequency = 20 #Hz
upper_frequency = 4000 #Hz

#Read the byte string
tensor_bstr = tf.io.read_file(filename1)

#Convert the byte string in a TF tensor
spectrogram = tf.io.parse_tensor(tensor_bstr, out_type=tf.float32)


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

mel_spectrogram.set_shape(spectrogram.shape[:-1].concatenate( 
        linear_to_mel_weight_matrix.shape[-1:]))

log_mel_spectrogram = tf.math.log(mel_spectrogram + 1e-6)


#Compute the MFCCs
mfccs = tf.signal.mfccs_from_log_mel_spectrograms(
        log_mel_spectrogram)[:,:10]

#Store the MFCC on disk
tf.io.write_file(filename2, mfccs)

#Measure the size of the output file
print('size: ', os.path.getsize(filename2),' bytes')