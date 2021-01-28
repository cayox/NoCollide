from queue import LifoQueue
from threading import Thread


class CanConfig:
    """
    Class to better store config details of the can bus if necessary
    """
    # TODO: Implement CAN Config
    pass


class CanBus:
    def __init__(self, conf: CanConfig, q_size: int = 1):
        # Queue to always save the last `q_size` amount of speeds
        self.q = LifoQueue(maxsize=q_size)  # LIFO
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

            if speed is None:  # these 2 lines are needed in case the retrieving of the speed cannot be a blocking function
                continue       # so that None (or another default value) is not put into the Queue

            if self.q.full():
                _ = self.q.get()  # remove oldest value
            self.q.put(speed)

    def get_speed(self) -> float:
        """
        Method to retrieve the speed from the queue

        :returns: the latest speed sent via CAN
        :rtype: float
        """
        return self.q.get()
