from sensor_processing import GrayscaleMod
from time import sleep
from picarx_improved import Picarx


class LineFollower():
    def __init__(self):
        self.grayscale = GrayscaleMod()
        self.car = Picarx()
        self.max_turn = 30

    def set_refs(self):
        input("Set robot on line where left sensor is on one color and middle sensor is on the other color.")
        self.grayscale.set_reference()
        sleep(0.5)
        print("\nReferences Set: Difference: {self.grayscale.reference_diff} Threshold: {self.grayscale.reference_value}")
        line_color = input("Are you following a Black line or White line? Enter B or W")
        if line_color.upper() == 'B':
            self.grayscale.bk_on_w = True
        elif line_color.upper() == 'W':
            self.grayscale.bk_on_w = False
        

    def steer_car(self):
        robot_pos = self.grayscale.interpret_readings()
        turn_angle = self.max_turn * robot_pos

        self.car.set_dir_servo_angle(turn_angle)
        


        
