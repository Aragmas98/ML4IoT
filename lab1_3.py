from picamera import PiCamera

camera = PiCamera()
camera.capture('./outputs/l1_3_photo.png')
camera.close()