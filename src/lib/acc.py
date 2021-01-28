from typing import *
import time

from .sensor import Sensor, SensorGroup
from .canbus import CanBus, CanConfig
from .data import Data


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
    def __init__(self, can_config: CanConfig, sensors: SensorGroup, ttc_times: Union[TtcTimes, None] = None):
        self.can_bus = CanBus(can_config)

        self.sensors = sensors

        if ttc_times is None:
            self.ttc_times = TtcTimes(0.6, 1.6, 3.0)
        else:
            self.ttc_times = ttc_times

    def run(self):
        self.can_bus.run_forever()

        v_old = Data(0, 0)
        front_old = Data(0, 0)
        v_front_old = Data(0, 0)

        while True:
            # time.sleep(0.2)
            v = self.can_bus.get_speed()
            print(f"v: {v}")
            a = v.calc_acc(v_old)
            print(f"a: {a}")

            v_old = v

            front = self.sensors.get_closest()
            print(f"Closest Object: {front}")
            if front == 1:
                continue

            v_front = front.calc_v(front_old)
            # print(f"v_front: {v_front}")
            a_front = v_front.calc_acc(v_front_old)

            front_old = front
            v_front_old = v_front

            v_rel = v - v_front
            a_rel = a - a_front
            # print(f"v_rel: {v_rel}")

            if v_rel == 0:
                continue

            # https://www.sbes.vt.edu/gabler/publications/Kusano-Gabler-SAE-TTC_EDRs-2011-01-0576.pdf
            ttc = front.value / v.value
            # ttc = v.time - (1 / (2*v_rel.value)) * a_rel.value * (v.time ** 2)
            print(f"TTC: {ttc} s")
            if self.regulate(ttc):
                break

    def regulate(self, ttc: float) -> bool:
        if ttc <= self.ttc_times.warning:
            self.can_bus.warn()
        if ttc <= self.ttc_times.brake:
            self.can_bus.set_throttle(0)
            # brake intensity depending on the time to colision
            brake_factor = (ttc - self.ttc_times.emergency_brake) / (self.ttc_times.brake - self.ttc_times.emergency_brake)
            self.can_bus.set_brake(brake_factor)
            return True
        return False






