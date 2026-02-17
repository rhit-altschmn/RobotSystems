
from flask import Flask, Response
from picamera2 import Picamera2
import cv2
from time import sleep
from picarx_improved import Picarx
import numpy as np

app = Flask(__name__)

class LineCam():
    FRAME_W, FRAME_H = 320, 240

    ROI_Y_START = 160
    ROI_HEIGHT  = 80

    THRESH_VAL = 120
    INVERT     = True

    JPEG_QUALITY = 70

    IM_CENTER = 320

    

    WHITE_VAL = 2000
    BLACK_VAL = 100

    def __init__(self):
        print("[INIT] Initializing PiCar-X")
        px = Picarx()

        print("[INIT] Setting camera tilt to -35 deg")
        px.set_cam_tilt_angle(-35)
        sleep(0.4)  # let servo settle

        # ============================================================
        # Init Camera
        # ============================================================
        print("[INIT] Starting Picamera2")
        self.picam2 = Picamera2()
        self.picam2.configure(
            self.picam2.create_video_configuration(
                main={"size": (self.FRAME_W, self.FRAME_H), "format": "RGB888"}
            )
        )
        self.picam2.start()
        sleep(0.5)

        self.binary = None
        # self.line_sensor = [0,0,0]


        print("[INIT] Camera started")

    # ============================================================
    # Frame generator
    # ============================================================
    def gen_frames(self):
        while True:
            frame = self.picam2.capture_array()  # RGB888

            # --- grayscale ---
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # --- ROI (EXACT SAME AS LINE FOLLOWER) ---
            roi = gray[self.ROI_Y_START : self.ROI_Y_START + self.ROI_HEIGHT,: ]

            # --- threshold ---
            thresh_type = cv2.THRESH_BINARY_INV if self.INVERT else cv2.THRESH_BINARY
            _, self.binary = cv2.threshold(roi, self.THRESH_VAL, 255, thresh_type)

            # --- upscale for visibility ---
            vis = cv2.resize(self.binary,None,fx=2.0,fy=2.0,interpolation=cv2.INTER_NEAREST)

            ok, jpg = cv2.imencode(
                ".jpg",
                vis,
                [int(cv2.IMWRITE_JPEG_QUALITY), self.JPEG_QUALITY]
            )
            if not ok:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + jpg.tobytes()
                + b"\r\n"
            )

    def img_process(self):
        readings = [0,0,0]
        # 4. Perform Canny edge detection
        # minVal and maxVal are the lower and upper thresholds for the hysteresis procedure
        edges = cv2.Canny(self.binary, 50, 150)

        # print(f"Edge image size {edges.shape}")

        # 5. Get the coordinates of edge pixels
        # np.argwhere returns a list of coordinates for non-zero pixels
        # The result is in (row, column) format, which corresponds to (y, x)
        edge_pixels = np.argwhere(edges > 0)

        # print(f"Found {len(edge_pixels)} edge pixels. \n {edge_pixels}")
        
        left_px = edge_pixels[0,1]
        right_px = edge_pixels[1,1]

        left_off = self.IM_CENTER - left_px
        right_off = right_px -self.IM_CENTER

        total_off = right_off - left_off


        print(f"Left px: {left_px}   Right px: {right_px}   Left off: {left_off}  Right off: {right_off} Total offset: {total_off}")

        if np.abs(total_off) <= 25: 
            readings = [self.WHITE_VAL,self.BLACK_VAL,self.WHITE_VAL]
        elif total_off < -80:
            readings = [self.BLACK_VAL,self.WHITE_VAL,self.WHITE_VAL]
        elif total_off > 80:
            readings = [self.WHITE_VAL,self.WHITE_VAL,self.BLACK_VAL]
        elif total_off < -25:
            readings = [self.BLACK_VAL,self.BLACK_VAL,self.WHITE_VAL]
        elif total_off > 25:
            readings = [self.WHITE_VAL,self.BLACK_VAL,self.BLACK_VAL]

        print(f"sensor read: {readings}")

    
        read_var = [self.bk_on_w,None,None] 

        '''
        bl_on_w = true
        line in middle: r0 = H r1 = L r2 = H
        line on left: r0 = L r1 = H r2 = H 
        line on right: r0 = H r1 = H r2 = L

        bl_on_w = false   white line black ground
        line in middle: r0 = L r1 = H r2 = L
        line on right: r0 = L r1 = L r2 = H 
        line on left: r0 = H r1 = L r2 = L
        
        H -> white  L -> black 
        +# means white left black right
        -# means black left white right
        '''
        if (readings[0] - readings[1]) > self.reference_diff:
            read_var[1] = 1
        elif (readings[0] - readings[1]) < -self.reference_diff:
            read_var[1] = -1
        else:
            read_var[1] = 0

        if (readings[1] - readings[2]) > self.reference_diff:
            read_var[2] = 1
        elif (readings[1] - readings[2]) < -self.reference_diff:
            read_var[2] = -1
        else:
            read_var[2] = 0

        match read_var:
            case [True,0,0] if readings[1] > self.reference_value: # BonW WWW
                if self.was_last_left:
                    return -1
                else:
                    return 1
            case [True, 0, 0] if readings[1] < self.reference_value: # BonW BBB
                return 0.0
            
            
            case[True,1,0]: # wbb
                self.was_last_left = False
                return 0.25
            case[True,0,1]: # wwb
                self.was_last_left = False
                return 0.5
            case[True,-1,0]: # bww
                self.was_last_left = True
                return -0.5
            case[True,0,-1]: # bbw
                self.was_last_left = True
                return -0.25
            case[True,1,-1]: # wbw
                return 0.0
            
    
    def steer_car(self):
        robot_pos = self.img_process()
        turn_angle = self.max_turn * robot_pos

        if turn_angle != self.turn_angle:
            self.turn_angle = turn_angle
            self.car.set_dir_servo_angle(int(turn_angle))
        
        self.car.forward(10)
        sleep(0.005)


    def shut_down(self):
        self.car.close()
        



    # ============================================================
    # Routes
    # ============================================================
    @app.route("/")
    def index():
        return (
            "<h2>PiCar-X Threshold Debug Stream</h2>"
            "<p><a href='/video'>Open /video</a></p>"
            "<p>ROI: y=160:240, THRESH_BINARY_INV</p>"
        )

    @app.route("/video")
    def video(self):
        return Response(
            self.gen_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    # ============================================================
    # Main
    # ============================================================
if __name__ == "__main__":
    cf = LineCam()
    print("[MAIN] Threshold stream running on port 8080")
    cf.app.run(host="0.0.0.0", port=8080, threaded=True)
    try:
        while True:
            cf.steer_car()
    except KeyboardInterrupt:
        cf.shut_down()

