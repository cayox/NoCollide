from datetime import datetime, timedelta
from typing import List, Union
import queue
from threading import Thread
from abc import abstractmethod
import time

# from smbus2 import SMBus
from .data import Distance


class AbstractSensor:
    @abstractmethod
    def measure(self, rec_bias_corr: bool = True):
        pass

    @abstractmethod
    def read_measurements(self) -> int:
        pass

    @abstractmethod
    def close(self):
        pass


class Sensor(AbstractSensor):
    """
    The Class that handles a LiDAR Sensor

    :param: i2c_bus: the bus number on which the sensor is running, defaults to Bus 1
    :type i2c_bus: int
    """

    def __init__(self, i2c_bus: int = 1, max_range: int = 50):
        self._addr = 0x62
        self.busnum = i2c_bus
        # self._bus = SMBus(self.busnum)
        self._mode = 0
        self.max_range = max_range
    
    def __str__(self):
        return f"Sensor on Bus {self.busnum} with i2c address {self._addr}"

    def __repr__(self):
        return f"Sensor(i2c_bus={self.busnum})"

    def __enter__(self):
        self.configure()
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.close()
        except OSError:
            pass

    @property
    def addr(self):
        return self._addr

    @property
    def mode(self):
        return self._mode

    def _sensor_ready(self, timeout: int = 200):
        """
        Method that blocks until the sensor is ready or the timeout is reached

        :param timeout: the max time in ms which should be waited until the sensor is ready
        :type timeout: int
        """

        # TODO: Not the most efficient way to check for timeout
        starttime = datetime.now()
        
        status = self._bus.read_byte_data(self._addr, 0x01)
        while status & 0x01:
            if datetime.now() - starttime > timedelta(milliseconds=timeout):
                raise TimeoutError("Cannot initialize the Sensor; Sensor is always busy")
            status = self._bus.read_byte_data(self._addr, 0x01)
    
    def change_addr(self, new_addr: int):
        """
        Method to change the I2C Address of the sensor

        :param new_addr: the new address that should be set
        :type new_addr: int
        """

        # read high byte
        id_high = self._bus.read_byte_data(self._addr, 0x16)
        # read low byte
        id_low = self._bus.read_byte_data(self._addr, 0x16)

        # unlock address lock
        self._bus.write_byte_data(self._addr, 0x18, id_high)
        self._bus.write_byte_data(self._addr, 0x19, id_low)

        # write new address to register
        self._bus.write_byte_data(self._addr, 0x1a, new_addr)

        # enable new adress using the default address
        self._bus.write_byte_data(self._addr, 0x1e, 0)
        self._addr = new_addr

    def configure(self, mode: int = 0):
        """
        Method to initialize the sensor to different modi. Must be done before the sensor can be used
        
        **configuration:**  Defaults to **0**.

        | **0**: Default mode, balanced performance
        | **1**: Short range, high speed. Uses ``0x1d`` maximum acquisition count
        | **2**: Default range, higher speed short range. Turns on quick termination
        |        detection for faster measurements at short range (with decreased accuracy)
        | **3**: Maximum range. Uses ``0xff`` maximum acquisition count
        | **4**: High sensitivity detection. Overrides default valid measurement detection
        |        algorithm, and uses a threshold value for high sensitivity and noise
        | **5**: Low sensitivity detection. Overrides default valid measurement detection
        |        algorithm, and uses a threshold value for low sensitivity and noise

        :param mode: the selected mode
        :type mode: int
        """

        self._mode = mode if 0 <= mode <= 6 else 0

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

        self._bus.write_byte_data(self._addr, 0x02, sig_count_max)
        self._bus.write_byte_data(self._addr, 0x04, acq_conf_reg)
        self._bus.write_byte_data(self._addr, 0x12, ref_count_max)
        self._bus.write_byte_data(self._addr, 0x1c, threshold_bypass)
        
    def measure(self, rec_bias_corr: bool = True):
        """
        Method to tell the sensor to take a measurement

        :param rec_bias_corr: Wether the measurement should be taken with or without receiver bias correction; defaults to True
        :type rec_bias_corr: bool
        """
        self._bus.write_byte_data(self._addr, 0x00, 0x04 if rec_bias_corr else 0x03)
    
    def read_measurements(self) -> int:
        """
        Method to obtain the measured distance in cm

        :returns: the measured value in cm. Returns 0 if timeouted
        :rtype: int
        """

        res = self._bus.read_byte_data(self._addr, 0x0f)
        res << 8
        res |= self._bus.read_byte_data(self._addr, 0x10)
        return res

    def close(self):
        """
        Method to close the bus
        """
        self._bus.close()


class SensorGroup:
    """
    Class to connect to multiple sensors at once.

    This class can be used in a context manager (``with`` statement).
    It returns itself and then all :py:class:`Sensors <.Sensor>` which are being set (default: 3).

    **If not used in a** ``with`` **-Statement the bus must be closed manually using the** :py:meth:`close() <.SensorGroup.close>` **method**

    .. code-block:: python

        with SensorGroup(i2c_bus=1) as (group, *sensors):
            ...

    :param i2c_bus: the raspberry pi bus the sensors are running on
    :type i2c_bus: int
    :param sensor_names: a list of names, to identify the sensors. Defaults to ``["left", "center", "right"]`` if ``None``
    :type sensor_names: Union[List[str], None]
    :param init_mode: the mode the sensors should be initialised with. Defaults to mode 0. See :py:meth:`Sensor.configure() <.Sensor.configure>` method
    :type init_mode: int
    """

    def __init__(self, i2c_bus: int, sensors: Union[Sensor, None] = None, sensor_names: Union[List[str], None] = None, init_mode: int = 0):
        self.bus = i2c_bus
        self.mode = init_mode

        if sensor_names is None:
            self.sensor_names = ["left", "center", "right"]
        else:
            self.sensor_names = sensor_names
        self._sensors = sensors

        self._queues = []
        self._threads = []

        if self._sensors is None:
            if sensor_names is None:
                raise ValueError("When setting the sensors manually the names must be set as well")
            self._set_sensors()
        else:
            if len(self.sensor_names) != len(self._sensors):
                raise ValueError("Sensors and names do not match in length")

            for sensor, name in zip(self._sensors, self.sensor_names):
                self.__setattr__(name, sensor)

        self.max_range = 0
        for s in self._sensors:
            if s.max_range > self.max_range:
                self.max_range = s.max_range

    def _set_sensors(self):
        default_addr = 0x62
        for addr, name in enumerate(self.sensor_names, default_addr):
            sensor_name = f"sensor_{name}"
            sensor = Sensor(i2c_bus=self.bus)
            sensor.change_addr(addr)
            sensor.configure(self.mode)
            self._sensors.append(sensor)
            self.__setattr__(sensor_name, sensor)

    def __str__(self):
        return f"{len(self.sensor_names)} Sensors on Bus {self.busnum}"

    def __repr__(self):
        return f"Sensor(i2c_bus={self.busnum}, {self.sensor_names}, init_mode={self.mode})"

    def __enter__(self):
        return (self, *self._sensors)

    def __exit__(self, type, value, traceback):
        self.close()

    def _measure_sensor(self, sensor: Sensor, queue: queue.Queue):
        time_before = time.perf_counter()
        while True:
            sensor.measure()
            time_now = time.perf_counter()
            queue.put(Distance(sensor.read_measurements(), time_now - time_before))
            time_before = time_now

    def start(self):
        """
        Method to start the measurements of the sensors
        """
        for s in self.sensors:
            q = queue.Queue()
            self._queues.append(q)

            thread = Thread(target=self._measure_sensor, args=[s, q], daemon=True)
            self._threads.append(thread)
            thread.start()

    def get_closest(self) -> Distance:
        closest = None
        for i, q in enumerate(self._queues):
            try:
                val = q.get()
            except queue.Empty:
                continue

            if closest is None or (val < closest and val != 0):
                closest = val
            else:
                closest = Distance(self.max_range, 0)
        return closest

    def close(self):
        """
        Method do close and delete all sensors from the group. This method is also called when exiting the ``with``-Statement
        """

        for sensor, name in zip(self._sensors, self.sensor_names):
            try:
                sensor.close()
            except OSError:
                pass
            self.__delattr__(name)
        self.sensor_names = []
        self._sensors = []

    @property
    def sensors(self):
        return self._sensors

    def set_mode(self, mode_num: int, sensors: List[str] = None):
        """
        Method to set the mode for specific or all Sensors in the group

        :param mode_num: the mode number, referring to the mode if the :py:meth:`configure() <.Sensor.configure>` method of the :class:`.Sensor`
        :param sensors: the sensornames of which the mode should be changed
        :raises TypeError: TypeError when the is no such sensor in the group
        """
        if sensors is None or len(sensors) == 0:
            sensors = self.sensor_names

        for sensor_name in sensors:
            if not hasattr(self, sensor_name):
                raise TypeError(f"The SensorGroup does not have a Sensor called {sensor_name}")
            sensor = self.__getattribute__(sensor_name)
            if not isinstance(sensor, Sensor):
                raise TypeError(f"The SensorGroup does not have a Sensor called {sensor_name}")

            sensor.configure(mode_num)

        
if __name__ == "__main__":
    import time    

    with Sensor() as s:
        s.configure()

        while True:
            s.measure()
            print(s.read_measurements())
            time.sleep(0.1)