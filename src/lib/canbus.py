from queue import Queue
from threading import Thread
import time
from abc import abstractmethod

from .data import Data


class CanConfig:
    """
    Class to better store config details of the can bus if necessary
    """
    # TODO: Implement CAN Config
    pass


class Driver:
    @abstractmethod
    def get_speed(self) -> Data:
        pass

    @abstractmethod
    def set_throttle(self, val: float):
        pass

    @abstractmethod
    def set_brake(self, val):
        pass

    @abstractmethod
    def warn(self):
        pass


class CanBus(Driver):
    def __init__(self, conf: CanConfig, q_size: int = 1):
        # Queue to always save the last `q_size` amount of speeds
        self.q = Queue(maxsize=q_size)  # LIFO
        self.conf = conf
        # further init code to setup the bus
        # ...

        # run canbus in sperate thread so that always the newest data can be retrieved
        self.thread = Thread(target=self.run_forever, daemon=True)
        self.thread.start()

        self.last_rx_time = 0

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
            self.q.put(Data(speed, rx_time - self.last_rx_time))
            self.last_rx_time = rx_time

    def get_speed(self) -> Data:
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