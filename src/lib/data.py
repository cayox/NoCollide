from __future__ import annotations


class Data:
    def __init__(self, value: float, time: float):
        self.value = value
        self.time = time

    def __str__(self):
        return f"{self.value} @ {self.time} s"

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


class Speed(Data):

    def __str__(self):
        return f"{self.value} m/s @ {self.time} s"

    @property
    def speed(self):
        return self.value

    def acceleration(self, other: Speed) -> Data:
        delta_t = (self.time - other.time)
        if delta_t == 0:
            return Speed(0, 0)
        return Speed(self.value / (self.time - other.time), self.time)


class Distance(Data):

    def __str__(self):
        return f"{self.value} m @ {self.time} s"

    @property
    def distance(self):
        return self.value

    def velocity(self, other: Distance) -> Speed:
        return Speed((other.value - self.value) / (self.time - other.time), self.time)
