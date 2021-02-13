from .nocollide import NoCollide
from .sensor import SensorGroup, SensorInterface
from .data import Distance


class SimNoCollide(NoCollide):
    """
    A class to use the NoCollide in the Carla-Simulator. Simply integrates the HUD of the simulator to warn via the
    HUD rather than to warn via some kind of Bus

    :param hud: The HUD of the Simulation
    :param args: Arguments to be passed to the parent class
    :param kwargs: Keyword arguments to be passed to the parent class
    """
    def __init__(self, hud, *args, **kwargs):
        super(SimNoCollide, self).__init__(*args, **kwargs)

        self._hud = hud

    def warn(self, ttc: float):
        """
        Overwrites the parent warn Method to warn via the HUD rather than some kind of Bus
        :param ttc: the Time-to-Collision in seconds
        :type ttc: float
        """
        self.ttc = ttc
        if ttc < 0:
            return

        if ttc <= self.ttc_times.too_late:
            self._hud.color_notification(f"Too Late", (255, 0, 0), 0.2)
        elif ttc <= self.ttc_times.brake:
            self._hud.color_notification(f"Brake!", (255, 69, 0), 0.2)
        elif ttc <= self.ttc_times.warning:
            self._hud.color_notification(f"Warning!", (255, 255, 0), 0.2)


class SimSensor(SensorInterface):
    """
    A class to implement the Carla-Simulator object detection sensor. Due to the constant pushing nature of the Carla sensor,
    the last retrieved value and time must be saved to be ready when the NoCollide Algorithm requests the Value.

    :param sensor: the Carla sensor to use
    :param max_range: the maximum range of the Carla Sensor
    """
    def __init__(self, sensor, max_range=40):
        self.data = None
        self.sensor = sensor
        self.max_range = max_range

        self.val = 0
        self.time = 0

    def close(self):
        pass

    def read_measurements(self) -> Distance:
        """
        The method ot retrieve the newest Data of the Sensor. If the Carla Sensor hasn't measured anything yet,
        a :py:class:`Distance <.data.Distance>` object will be returned with the maximum range.
        :return: the newest Distance measured by the Carla sensor
        :rtype: :py:class:`Distance <.data.Distance>`
        """
        if self.val == 0:
            d = Distance(self.max_range, self.time)
        else:
            d = Distance(self.val, self.time)
        return d

    def measure(self, rec_bias_corr: bool = True):
        pass

    def configure(self, mode: int):
        pass

    def change_addr(self, addr: int):
        pass

    def callback(self, data):
        """
        The callback method that is called, whenever the Carla sensor has measured new data. Simply stores the data,
        so taht i can be requested any time

        :param data: the data measured by the carla sensor
        """
        self.time = data.timestamp
        self.val = data.distance

    def destroy(self):
        """
        Method to destroy the Sensor to free up memory when the simulation has ended
        """
        self.sensor.destroy()

    def listen(self):
        """
        A Method to tell the Carla sensor to use the :py:meth:`callback() <.SimSensor.callback>` method whenever a new
        value is measured
        """
        self.sensor.listen(self.callback)

    def stop(self):
        """
        A method that is needed when stopping the simulation.
        """
        pass


class SimSensorGroup(SensorGroup):
    """
    Class to overwrite the :py:class:`SensorGroup <.sensor.SensorGroup>` class to use the simulated sensor when retrieving the distance
    """
    def get_closest(self) -> Distance:
        """
        Class to overwrite the :py:meth:`get_closest() <.sensor.SensorGroup.get_closest>` method to use the simulated sensor when retrieving the distance
        :return:
        """
        closest = None
        for sensor in self._sensors:
            val = sensor.read_measurements()

            if closest is None or val < closest:
                closest = val

        if closest is None:
            return Distance(self.max_range, 0)
        return closest