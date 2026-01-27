try:
    from robot_hat import Pin, ADC, PWM, Servo, fileDB
    # from robot_hat import Grayscale_Module, Ultrasonic, utils
    on_the_robot = True
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) #
    # MAKE SURE YOU ARE cd picarx before running!!!!!!!!!!!!!!!
    from sim_robot_hat import Pin, ADC, PWM, Servo, fileDB
    # from sim_robot_hat import Grayscale_Module, Ultrasonic, utils
    on_the_robot = False


class LineSensor(object):
    """3 channel Grayscale Module"""

    LEFT = 0
    """Left Channel"""
    MIDDLE = 1
    """Middle Channel"""
    RIGHT = 2
    """Right Channel"""

    def __init__(self, pin0, pin1, pin2, reference: int = None):
        """
        Initialize Grayscale Module

        :param pin0: ADC object or int for channel 0
        :type pin0: robot_hat.ADC/int
        :param pin1: ADC object or int for channel 1
        :type pin1: robot_hat.ADC/int
        :param pin2: ADC object or int for channel 2
        :type pin2: robot_hat.ADC/int
        :param reference: reference voltage
        :type reference: 1*3 list, [int, int, int]
        """
        grayscale_pins = [pin0, pin1, pin2]
        adc0, adc1, adc2 = [ADC(pin) for pin in grayscale_pins]

        self.pins = (adc0, adc1, adc2)
        for i, pin in enumerate(self.pins):
            if not isinstance(pin, ADC):
                raise TypeError(f"pin{i} must be robot_hat.ADC")
        

    
    def read(self, channel: int = None) -> list:
        """
        read a channel or all datas

        :param channel: channel to read, leave empty to read all. 0, 1, 2 or Grayscale_Module.LEFT, Grayscale_Module.CENTER, Grayscale_Module.RIGHT 
        :type channel: int/None
        :return: list of grayscale data
        :rtype: list
        """
        if channel == None:
            return [self.pins[i].read() for i in range(3)]
        else:
            return self.pins[channel].read()