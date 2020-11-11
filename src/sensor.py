from smbus2 import SMBus
from datetime import datetime, timedelta


class Sensor:
    """
    The Class that handles a LiDAR Sensor

    :param: i2c_bus: the bus number on which the sensor is running, defaults to Bus 1
    :type i2c_bus: int
    """

    def __init__(self, i2c_bus: int = 1):
        self.addr = 0x62
        self.busnum = i2c_bus
        self._bus = SMBus(self.busnum)
        self.mode = 0
    
    def __str__(self):
        return f"Sensor on Bus {self.busnum}"

    def __repr__(self):
        return f"Sensor(i2c_bus={self.busnum})"

    def __enter__(self):
        self.configure()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

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
            if datetime.now() - starttime > timedelta(milliseconds=timeout):
                raise TimeoutError("Cannot initialize the Sensor; Sensor is always busy")
            status = self._bus.read_byte_data(self.addr, 0x01)
    
    def change_addr(self, new_addr: int):
        """
        Method to change the I2C Address of the sensor

        :param new_addr: the new address that should be set
        :type new_addr: int
        """
        # read high byte
        id_high = self._bus.read_byte_data(self.addr, 0x16)
        # read low byte
        id_low = self._bus.read_byte_data(self.addr, 0x16)

        # unlock address lock
        self._bus.write_byte_data(self.addr, 0x18, id_high)
        self._bus.write_byte_data(self.addr, 0x19, id_low)

        # write new address to register
        self._bus.write_byte_data(self.addr, 0x1a, new_addr)

        # enable new adress using the default address
        self._bus.write_byte_data(self.addr, 0x1e, 0)

    def get_mode(self):
        """
        Method to retreive the measurement mode the sensor is configured

        :returns: the mode number
        :rtype: int
        """
        return self.mode

    def configure(self, mode: int = 0):
        """
        Method to initialize the sensor to different modi. Must be done before the sensor can be used
        
        **configuration:**  Default 0.

        0. Default mode, balanced performance.
        1. Short range, high speed. Uses 0x1d maximum acquisition count.
        2. Default range, higher speed short range. Turns on quick termination
           detection for faster measurements at short range (with decreased
           accuracy)
        3. Maximum range. Uses 0xff maximum acquisition count.
        4. High sensitivity detection. Overrides default valid measurement detection
           algorithm, and uses a threshold value for high sensitivity and noise.
        5. Low sensitivity detection. Overrides default valid measurement detection
           algorithm, and uses a threshold value for low sensitivity and noise.

        :param mode: the selected mode
        :type mode: int
        """

        self.mode = mode if 0 <= mode <= 6 else 0

        sig_count_max = 0x80
        acq_conf_reg = 0x08
        ref_count_max = 0x05
        threshold_bypass = 0x00

        if mode == 1:
            # short range, high speed
            sig_count_max = 0x1d
            acq_conf_reg = 0x00
            ref_count_max = 0x03
            threshold_bypass = 0x00
        elif mode == 2:
            # default range, higher speed short range
            sig_count_max = 0x80
            acq_conf_reg = 0x00
            ref_count_max = 0x03
            threshold_bypass = 0x00
        elif mode == 3:
            # max range
            sig_count_max = 0xff
            acq_conf_reg = 0x08
            ref_count_max = 0x05
            threshold_bypass = 0x00
        elif mode == 4:
            # high sensitivity detection, high erroneous measurements
            sig_count_max = 0x80
            acq_conf_reg = 0x08
            ref_count_max = 0x05
            threshold_bypass = 0x80
        elif mode == 5:
            # Low sensitivity detection, low erroneous measurements
            sig_count_max = 0x80
            acq_conf_reg = 0x08
            ref_count_max = 0x05
            threshold_bypass = 0xb0
        elif mode == 6:
            # short range, high speed, higher error
            sig_count_max = 0x04
            acq_conf_reg = 0x01
            ref_count_max = 0x03
            threshold_bypass = 0x00


        self._bus.write_byte_data(self.addr, 0x02, sig_count_max)
        self._bus.write_byte_data(self.addr, 0x04, acq_conf_reg)
        self._bus.write_byte_data(self.addr, 0x12, ref_count_max)
        self._bus.write_byte_data(self.addr, 0x1c, threshold_bypass)
        
    def measure(self, rec_bias_corr: bool = True):
        """
        Method to tell the sensor to take a measurement

        :param rec_bias_corr: Wether the measurement should be taken with or without receiver bias correction; defaults to True
        :type rec_bias_corr: bool
        """
        self._bus.write_byte_data(self.addr, 0x00, 0x04 if rec_bias_corr else 0x03)
    
    def read_measurements(self) -> int:
        """
        Method to obtain the measured distance in cm

        :returns: the measured value in cm. Returns 0 if timeouted
        :rtype: int
        """

        res = self._bus.read_byte_data(self.addr, 0x0f)
        res << 8
        res |= self._bus.read_byte_data(self.addr, 0x10)
        return res

    def close(self):
        """
        Method to close the bus
        """
        self._bus.close()
        
        
if __name__ == "__main__":
    import time    

    with Sensor() as s:
        s.configure()

        while True:
            s.measure()
            print(s.read_measurements())
            time.sleep(0.1)