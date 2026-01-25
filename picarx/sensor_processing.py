from sensors import LineSensor



class GrayscaleMod():
    LEFT = 0
    """Left Channel"""
    MIDDLE = 1
    """Middle Channel"""
    RIGHT = 2
    """Right Channel"""

    REFERENCE_DEFAULT = 1000

    def __init__(self, sensitivity: int = None, polarity: bool = True):
        
        self.sensor = LineSensor()

        self.bk_on_w = polarity  #black line on white floor true
        self.reference_diff = sensitivity
        self.reference_value = self.REFERENCE_DEFAULT



    def set_reference(self):
        """
        Get Set reference value

        :param ref: reference value, None to get reference value
        :type ref: list
        :return: reference value
        :rtype: list
        """
        left_val = self.sensor.read(self.LEFT)
        mid_val = self.sensor.read(self.MIDDLE)

        diff = abs(left_val - mid_val)

        if self.reference_diff == None:
            self.reference_diff = diff*0.7

        if diff < 500:
            self.reference_value = self.REFERENCE_DEFAULT
        else:
            if left_val < mid_val:
                threshold = left_val + (diff/2)
            else:
                threshold = mid_val + (diff/2)
            
            self.reference_value = threshold

    def read_status(self, datas: list = None) -> list:
        """
        Read line status

        :param datas: list of grayscale datas, if None, read from sensor
        :type datas: list
        :return: list of line status, 0 for white, 1 for black
        :rtype: list
        """
        if self.reference_value == None:
            raise ValueError("Reference value is not set")
        if datas == None:
            datas = self.sensor.read()
        return [0 if data > self.reference_value else 1 for i, data in enumerate(datas)]
    
    def interpret_readings(self):
        readings = self.sensor.read()
        
        '''
        bl_on_w = true
        line in middle: r0 = H r1 = L r2 = H
        line on left: r0 = L r1 = H r2 = H 
        line on right: r0 = H r1 = H r2 = L
        
        '''
        #if (readings[0] - readings[1]) > :

















