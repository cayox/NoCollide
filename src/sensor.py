from smbus2 import SMBus



class Sensor:
    """
    The Class that handles the LiDAR Sensor

    :param i2c_bus: the bus number on which the sensor is running. Defaults to Bus 1
    :type i2c_bus: int
    """
    def __init__(self, i2c_bus: int = 1):
        self.addr = 0x62
        self.value_regs = [0x0f, 0x10]
        self.busnum = i2c_bus
        self.bus = SMBus(self.busnum)


    def initialize(self):
        """
        Method to initialize the sensor. Must be done before the sensor can be used
        """
        self.bus.write_byte_data(self.addr, 0x00, 0x04)
        res = self.bus.read_byte_data(self.addr, 0x01)
        while res & 0x01:
            res = self.bus.read_byte_data(self.addr, 0x01)
        
    def measure(self) -> int:
        """
        Method to obtain the measured distance in cm

        :returns: the measured value in cm
        :rtype: int
        """

        res = self.bus.read_byte_data(self.addr, 0x0f)
        res << 8
        res += self.bus.read_byte_data(self.addr, 0x10)
        return res
        






