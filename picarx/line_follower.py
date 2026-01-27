from sensor_processing import GrayscaleMod
from time import sleep
from picarx_improved import Picarx
import logging
from logdecorator import log_on_start, log_on_error, log_on_end

logging_format = "%(asctime)s: Line: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)
class LineFollower():
    
    def __init__(self):
        self.grayscale = GrayscaleMod()
        self.car = Picarx()
        self.max_turn = 30
        self.turn_angle = 0

    @log_on_start(logging.DEBUG, "Start Setting References")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    @log_on_end(logging.DEBUG, "References set: Black line? {self.grayscale.bk_on_w}")
    def set_refs(self):
        input("\nSet robot on line where left sensor is on one color and middle sensor is on the other color.  ")
        self.grayscale.set_reference()
        sleep(0.5)
        print("\nReferences Set: Difference: {self.grayscale.reference_diff} Threshold: {self.grayscale.reference_value}")
        line_color = input("Are you following a Black line or White line? Enter B or W:  ")
        if line_color.upper() == 'B':
            self.grayscale.bk_on_w = True
        elif line_color.upper() == 'W':
            self.grayscale.bk_on_w = False
        else:
            self.grayscale.bk_on_w = None
            print("Not an option")
        
    @log_on_start(logging.DEBUG, "Steer Car")
    @log_on_error(logging.DEBUG, "Error: {e!r}")
    def steer_car(self):
        robot_pos = self.grayscale.interpret_readings()
        turn_angle = self.max_turn * robot_pos

        if turn_angle != self.turn_angle:
            self.turn_angle = turn_angle
            self.car.set_dir_servo_angle(int(turn_angle))
        
        self.car.forward(10)
        sleep(0.005)


    def shut_down(self):
        self.car.close()
        


if __name__ == "__main__":
    lf = LineFollower()

    lf.set_refs()
    if lf.grayscale.bk_on_w == None:
        print("Try again")
        lf.set_refs()
    try:
        while True:
            lf.steer_car()
    except KeyboardInterrupt:
        lf.shut_down()



    



        
