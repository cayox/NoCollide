from typing import *
import time
from .sensor import Sensor, SensorGroup
from .canbus import CanBus, CanConfig
from .data import Data, Distance


class FIFO(list):
    def __init__(self, size: int = 4, *args, **kwargs):
        super(FIFO, self).__init__(*args, **kwargs)
        self.max_size = size

        for _ in range(self.max_size):
            self.append(None)

    def add(self, obj: Any):
        if len(self) >= self.max_size:
            self.pop()

        self.insert(0, obj)

    def get(self) -> Any:
        elem = self.pop(0)
        return elem


class TtcTimes:
    def __init__(self, emergency_brake: float, brake: float, warning: float):
        if not emergency_brake < brake < warning:
            raise ValueError("emergency_brake < brake < warning not true")

        self.emergency_brake = emergency_brake
        self.brake = brake
        self.warning = warning


class ACC:
    def __init__(self,  can_config: CanConfig, sensors: SensorGroup, min_distance: float = 5.0, ttc_times: Union[TtcTimes, None] = None):
        self.can_bus = CanBus(can_config)

        self.sensors = sensors
        self.min_distance = min_distance

        if ttc_times is None:
            self.ttc_times = TtcTimes(0.6, 1.6, 3.0)
        else:
            self.ttc_times = ttc_times

    def run(self):
        self.can_bus.run_forever()

        old_distance_between = None
        file = open("test.csv", "w", newline="")
        file.write(";".join(["distance", "time", "velocity", "ttc"]) + "\n")

        while True:
            _ = self.can_bus.get_speed()

            distance_between = self.sensors.get_closest()
            if distance_between >= self.sensors.max_range or distance_between.value == 0 or old_distance_between is None:
                old_distance_between = distance_between
                continue


            delta_v = distance_between.velocity(old_distance_between)
            print(f"delta_v: {delta_v}")

            old_distance_between = distance_between

            # https://www.sbes.vt.edu/gabler/publications/Kusano-Gabler-SAE-TTC_EDRs-2011-01-0576.pdf
            ttc = distance_between.value / delta_v.value
            # ttc = v.time - (1 / (2*v.value)) * a.value * (v.time ** 2)
            print(f"TTC: {ttc} s")
            file.write(";".join([str(v).replace(".", ",") for v in [distance_between.value, distance_between.time, delta_v.value, ttc]]) + "\n")
            if self.regulate(ttc):
                break

    def regulate(self, ttc: float) -> bool:
        if ttc <= self.ttc_times.warning:
            self.can_bus.warn()
        if ttc <= self.ttc_times.brake:
            print("BRAKE!")
            self.can_bus.set_throttle(0)
            # brake intensity depending on the time to colision
            brake_factor = (ttc - self.ttc_times.emergency_brake) / (self.ttc_times.brake - self.ttc_times.emergency_brake)
            self.can_bus.set_brake(brake_factor)
            return True
        return False






