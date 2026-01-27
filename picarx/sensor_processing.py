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

        self.was_last_left = True



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
                    return -1.0
                else:
                    return 1.0
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
            
        
        



















