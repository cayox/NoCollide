from queue import Queue
from threading import Thread
import time
from abc import abstractmethod

from .data import Speed


class CanConfig:
    """
    Class to better store config details of the can bus if necessary
    """
    # TODO: Implement CAN Config
    pass


class Driver:
    """
    An interface to be used by the :class:`noCollide <.nocollide.NoCollide>` class get and set parameters regarding
    the vehicle
    """
    @abstractmethod
    def get_speed(self) -> Speed:
        """
        A method to retrieve the current speed of the car

        :return: the current speed of the car
        :rtype: Speed
        """
        pass

    @abstractmethod
    def set_throttle(self, val: float):
        """
        A method to set the throttle of the vehicle

        :param val: the throttle amount
        :type val: float
        """
        pass

    @abstractmethod
    def set_brake(self, val):
        """
        A method to set the brake amount of the vehicle

        :param val: the brake amount
        :type val: float
        """
        pass

    @abstractmethod
    def warn(self):
        """
        A method to warn the user for possible collisions
        """
        pass


class CanBus(Driver):
    def __init__(self, conf: CanConfig, q_size: int = 1):
        """
        An implementation of a CAN Bus to warn the user and controll the car if possible.

        :param conf: the CAN Bus configuration
        :type conf: :py:class: `CanConfig <.CanConfig>`
        :param q_size: the amount of recent values to store, when polling the speed of the vehicle. Defaults to 1
        :type q_size: int
        """
        # Queue to always save the last `q_size` amount of speeds
        self.q = Queue(maxsize=q_size)  # LIFO
        self.conf = conf
        # further init code to setup the bus
        # ...

        # run canbus in sperate thread so that always the newest data can be retrieved
        self.thread = Thread(target=self.run_forever, daemon=True)
        self.thread.start()

    def run_forever(self):
        """
        Method to keep in touch with the CAN-Bus. Runs in a thread, to avoid blocking
        """
        while True:
            speed = None  # TODO: get actual speed via CAN
            rx_time = time.perf_counter()

            if speed is None:  # these 2 lines are needed in case the retrieving of the speed cannot be a blocking function
                continue       # so that None (or another default value) is not put into the Queue

            if self.q.full():
                _ = self.q.get()  # remove oldest value
            self.q.put(Speed(speed, rx_time))

    def get_speed(self) -> Speed:
        """
        Method to retrieve the speed from the queue

        :returns: the latest speed sent via CAN
        :rtype: float
        """
        return self.q.get()

    def set_throttle(self, val: float):
        # TODO: send throttle via CAN
        pass

    def set_brake(self, val):
        # TODO: send brake via CAN
        pass

    def warn(self):
        # TODO: send warning via CAN
        pass