from picamera2 import Picamera2, Preview
import time
from picarx_improved import Picarx


picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
# picam2.start_preview(Preview.QTL)
picam2.start()

px = Picarx()

px.set_cam_tilt_angle(-35)

time.sleep(2)


picam2.capture_file("linetest.jpg")