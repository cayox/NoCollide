from __future__ import annotations


class Data:
    def __init__(self, value: float, time: float):
        self.value = value
        self.time = time

    def calc_acc(self, data_before: Data) -> Data:
        delta_t = (self.time - data_before.time)
        if delta_t == 0:
            return Data(0, 0)
        return Data(self.value / (self.time - data_before.time), self.time)

    def calc_v(self, data_before: Data) -> Data:
        delta_t = (self.time - data_before.time)
        if delta_t == 0:
            return Data(0, 0)
        return Data((self.value - data_before.value) / (self.time - data_before.time), self.time)

    def __str__(self):
        return f"{self.value} @ {self.time}s"

    def __sub__(self, other) -> Data:
        if isinstance(other, Data):
            return Data(self.value - other.value, self.time)
        return Data(self.value - other, self.time)

    def __add__(self, other) -> Data:
        if isinstance(other, Data):
            return Data(self.value + other.value, self.time)
        return Data(self.value + other, self.time)

    def __truediv__(self, other) -> Data:
        if isinstance(other, Data):
            return Data(self.value / other.value, self.time)
        return Data(self.value / other, self.time)

    def __mul__(self, other) -> Data:
        if isinstance(other, Data):
            return Data(self.value * other.value, self.time)
        return Data(self.value * other, self.time)

    def __eq__(self, other):
        if isinstance(other, Data):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other):
        if isinstance(other, Data):
            return self.value != other.value
        return self.value != other

    def __le__(self, other):
        if isinstance(other, Data):
            return self.value <= other.value
        return self.value <= other

    def __lt__(self, other):
        if isinstance(other, Data):
            return self.value < other.value
        return self.value < other

    def __ge__(self, other):
        if isinstance(other, Data):
            return self.value >= other.value
        return self.value >= other

    def __gt__(self, other):
        if isinstance(other, Data):
            return self.value > other.value
        return self.value > other
