import argparse
import tensorflow as tf
import time, datetime

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, help='input file name', required=True)
parser.add_argument('--output', type=str, help='output file name', required=True)
parser.add_argument('--normalize', type=bool, default=False, help='option to normalize temperature', required=False)
args = parser.parse_args()

def _bytes_feature(value):
  """Returns a bytes_list from a string / byte."""
  if isinstance(value, type(tf.constant(0))):
    value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_feature(value):
  """Returns a float_list from a float / double."""
  return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
  """Returns an int64_list from a bool / enum / int / uint."""
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

MIN_TEMP = 0
MAX_TEMP = 50

with tf.io.TFRecordWriter(args.output) as writer:
    with open(args.input, 'r') as f:

        data_line = f.readline()

        while data_line != None and data_line != "":
            data_line = data_line.split(',')
            
            strdate = data_line[0] + ' ' + data_line[1]
            datetimeobj=datetime.datetime.strptime(strdate,"%d/%m/%Y %H:%M:%S")
            timeobj = time.mktime(datetimeobj.timetuple())

            if args.normalize:
                temp = float(data_line[2]) / (MAX_TEMP - MIN_TEMP)
            else:
                temp = float(data_line[2])
            
            mapping = { 
                    'datetime': _float_feature(float(timeobj)), 
                    'temperature': _float_feature(temp), 
                    'humidity': _float_feature(float(data_line[3]))
                }
            example = tf.train.Example(features=tf.train.Features(feature=mapping))
            writer.write(example.SerializeToString())
            data_line = f.readline()