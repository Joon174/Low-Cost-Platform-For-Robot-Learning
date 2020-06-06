class VirtualServo:
    def __init__(self, pulse_width):
        super(VirtualServo, self).__init__()
        self.min_width, self.max_width = pulse_width
        self.max_range = 180
        self.min_range = 0
        
    def actuate(self, pwm_signal):
        return (pwm_signal-self.min_width)*(self.max_range)/(self.max_width-self.min_width)
    
    def setPin(self, pin_number):
        self.pin_number = pin_number
        return pin_number
