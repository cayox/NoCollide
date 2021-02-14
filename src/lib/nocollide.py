from typing import *
from abc import abstractmethod
from .sensor import SensorGroup
from .driver import Driver


class NoCollideInterface:
    @abstractmethod
    def calc(self):
        pass

    @abstractmethod
    def warn(self, ttc: float):
        pass


class TtcTimes:
    """
    A struct like class to enhance readability when storing Time-to-Collision values.
    ``too_late < brake < warning`` must be True

    :param too_late: The time after which an accident is unavoidable
    :type too_late: float
    :param brake: The time after which the driver must be braking to avoid an accident
    :type brake: float
    :param warning: The time after which the driver should be warned
    :type warning: float
    :param reaction_time: the reaction time that should be added to ```brake`` and ``warning``. Defaults to 0.5
    :type reaction_time: float
    """
    def __init__(self, too_late: float, brake: float, warning: float, reaction_time: float = 0.5):
        if not too_late < brake < warning:
            raise ValueError("too_late < brake < warning not true")

        self.too_late = too_late
        self.brake = brake + reaction_time
        self.warning = warning + reaction_time


class NoCollide(NoCollideInterface):
    """
    The class that calculates the acc and regulates the warning.

    :param driver: The configuration of the CAN-Bus to initialise
    :type driver: :py:class:`Driver <.canbus.Driver>`

    :param sensors: The sensor group, on which the calculation should be done
    :type sensors: :py:class:`SensorGroup <.sensor.SensorGroup>`

    :param ttc_times: The times which define when to warn based on the TTC (Time-to-collision). If None, the default
     TTC-Times will be used: ``TtcTimes(too_late=0.6, brake=1.6, warning=2.6)``
    :type ttc_times: Union[:py:class:`TtcTimes <.TtcTimes>`, None]
    """
    def __init__(self, driver: Driver, sensors: SensorGroup, ttc_times: Union[TtcTimes, None] = None):
        self.driver = driver

        self.sensors = sensors

        if ttc_times is None:
            self.ttc_times = TtcTimes(0.6, 1.6, 2.6)
        else:
            self.ttc_times = ttc_times

        self.ttc = 0
        self.old_distance_between = None

    def run(self, block: bool = True):
        """
        The method to start the calculation. Can be run blocking (in an endless loop) or not (1 calulcation only)

        :param block: wether the method should block or not
        :type block: bool
        """
        if not block:
            self.calc()
            return

        while True:
            self.calc()

    def calc(self):
        """
        The method that calculates the Time-to-Collision. Takes the Value of the sensor, that measures the closest object
        and calculates the relative velocity. The TTC results in dividing the distance by the relative velocity
        :return:
        """
        distance_between = self.sensors.get_closest()
        if distance_between >= self.sensors.max_range or distance_between.value == 0 or self.old_distance_between is None:
            self.old_distance_between = distance_between
            return

        # print(f"{distance_between}, {self.old_distance_between}")
        delta_v = distance_between.velocity(self.old_distance_between)
        print(f"delta_v: {delta_v}")

        self.old_distance_between = distance_between

        try:
            ttc = distance_between.value / delta_v.value
        except ZeroDivisionError:
            ttc = self.ttc
        self.warn(ttc)

    def warn(self, ttc: float):
        """
        The method to warn the user based on the Time-to-Collision.

        :param ttc: the Time-to-Collision
        :type ttc: float
        """
        self.ttc = ttc

        if ttc < 0:
            return

        if ttc <= self.ttc_times.warning:
            self.driver.warn()
        if ttc <= self.ttc_times.brake:
            print("BRAKE!")
            self.driver.set_throttle(0)
            # brake intensity depending on the time to colision
            brake_factor = (ttc - self.ttc_times.too_late) / (self.ttc_times.brake - self.ttc_times.too_late)
            self.driver.set_brake(brake_factor)
