from smbus2 import SMBus
from datetime import datetime, timedelta


class Sensor:
    """
    The Class that handles the LiDAR Sensor

    :param i2c_bus: the bus number on which the sensor is running. Defaults to Bus 1
    :type i2c_bus: int
    """
    def __init__(self, i2c_bus: int = 1):
        self.addr = 0x62
        self.busnum = i2c_bus
        self._bus = SMBus(self.busnum)

        # initialize the sensor so it is ready to use
        self.initialize()
    
    def __str__(self):
        return f"Sensor on Bus {self.busnum}"
    
    def __repr__(self):
        return f"Sensor(i2c_bus={self.busnum})"

    def _sensor_ready(self, timeout: int = 200):
        """
        Method that blocks until the sensor is ready or the timeout is reached

        :param timeout: the max time in ms which should be waited until the sensor is ready
        :type timeout: int
        """

        # TODO: Not the most efficient way to check for timeout
        starttime = datetime.now()
        
        status = self._bus.read_byte_data(self.addr, 0x01)
        while status & 0x01:
            if datetime.now() - starttime < timedelta(milliseconds=500):
                raise TimeoutError("Cannot initialize the Sensor; Sensor is always busy")
            status = self._bus.read_byte_data(self.addr, 0x01)


    def initialize(self, rec_bias_correction: bool = True):
        """
        Method to initialize the sensor. Must be done before the sensor can be used
        
        :param rec_bias_correction: wether the receiver bias correction should be enabled
        :type rec_bias_correction: bool
        """
        self._bus.write_byte_data(self.addr, 0x00, 0x04)
        self._sensor_ready(500)
        
    def measure(self, timeout: int = 200) -> int:
        """
        Method to obtain the measured distance in cm

        :param timeout: the max time in ms which should be waited until the sensor is ready
        :type timeout: int
        :returns: the measured value in cm. Returns 0 if timeouted
        :rtype: int
        """

        # wait until sensor is ready
        try:
            self._sensor_ready()
        except TimeoutError:
            return 0

        res = self._bus.read_byte_data(self.addr, 0x0f)
        res << 8
        res += self._bus.read_byte_data(self.addr, 0x10)
        return res

    def close(self):
        """
        Method to close the bus
        """
        self._bus.close()
        
        
if __name__ == "__main__":
    s = Sensor()

    while True:
        print(s.measure())






