from picamera import PiCamera
import tensorflow as tf 

filename1 = './outputs/l2_4_photo5.png'

camera = PiCamera()

camera.resolution = (640, 480)
camera.contrast = 20
camera.iso = 100
camera.brightness = 70

camera.capture(filename1)
camera.close()

myTensor = tf.io.read_file(filename1)
myTensor = tf.io.decode_jpeg(myTensor)
myTensor = tf.image.crop_to_bounding_box(myTensor,)