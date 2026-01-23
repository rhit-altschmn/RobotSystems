from picarx_improved import Picarx
from time import sleep
import logging
from logdecorator import log_on_start, log_on_end, log_on_error

# !!! MAKE SURE YOU ARE cd picarx before running !!!

try:
    import readchar
    on_robot = True
except:
    on_robot = False

manual = '''
\n\nPress keys on keyboard to control PiCar-X!
    w: Forward
    a: Turn left
    s: Backward
    d: Turn right
    i: Head up
    k: Head down
    j: Turn head left
    l: Turn head right
    ctrl+c: Press twice to exit the program
'''


logging_format2 = "%(asctime)s: Mover: %(message)s"
logging.basicConfig(format=logging_format2, level=logging.INFO,datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

class Moves():
    @log_on_start(logging.DEBUG, "Starting Mover Init")
    @log_on_error(logging.DEBUG, "Error init: {e!r}")
    @log_on_end(logging.DEBUG, "Finished Mover init")
    def __init__(self):
        self.px = Picarx()

        self.pan_angle = 0
        self.tilt_angle = 0
        self.drive_angle = 0
        
        self.speed = 80

        self.runtime = 0.5

    @log_on_start(logging.DEBUG, "Go forward")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def forward(self):
        self.px.set_dir_servo_angle(0)
        self.px.forward(self.speed)
        sleep(self.runtime)
        self.px.stop()
    
    @log_on_start(logging.DEBUG, "Go Backward")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def reverse (self):
        self.px.set_dir_servo_angle(0)
        self.px.backward(self.speed)
        sleep(self.runtime)
        self.px.stop()
    
    @log_on_start(logging.DEBUG, "Turn left go forward")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def front_left(self):
        self.px.set_dir_servo_angle(-30)
        self.px.forward(self.speed)
        sleep(self.runtime)
        self.px.stop()
    
    @log_on_start(logging.DEBUG, "Turn right go forward")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def front_right(self):
        self.px.set_dir_servo_angle(30)
        self.px.forward(self.speed)
        sleep(self.runtime)
        self.px.stop()

    
    
    @log_on_start(logging.DEBUG, "Head up")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def head_up(self):
        self.tilt_angle+=5
        if self.tilt_angle>30:
            self.tilt_angle=30
        self.px.set_cam_tilt_angle(self.tilt_angle)
            
    @log_on_start(logging.DEBUG, "Head down")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def head_down(self):
        self.tilt_angle-=5
        if self.tilt_angle<-30:
            self.tilt_angle=-30
        self.px.set_cam_tilt_angle(self.tilt_angle)
        
    @log_on_start(logging.DEBUG, "Head left")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def head_right(self):
        self.pan_angle+=5
        if self.pan_angle>30:
            self.pan_angle=30
        self.px.set_cam_pan_angle(self.pan_angle) 
    
    @log_on_start(logging.DEBUG, "Head Right")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def head_left(self):
        self.pan_angle-=5
        if self.pan_angle<-30:
            self.pan_angle=-30  
        self.px.set_cam_pan_angle(self.pan_angle)      

                
if __name__ == "__main__":
    c = Moves()
    try:
        print(manual)
        while True:
            if on_robot:
                key = readchar.readkey()
                key = key.lower()
            else: 
                move = input("Enter key: ")
                key = move[0]

            match key:
                case 'w':
                    c.forward()
                    print(manual)
                case 's':
                    c.reverse()
                    print(manual)
                case 'a':
                    c.front_left()
                    print(manual)
                case 'd':
                    c.front_right()
                    print(manual)
                case 'i':
                    c.head_up()
                    print(manual)
                case 'k':
                    c.head_down()
                    print(manual)
                case 'j':
                    c.head_left()
                    print(manual)
                case 'l':
                    c.head_right()
                    print(manual)

    except KeyboardInterrupt:
        c.px.reset()

