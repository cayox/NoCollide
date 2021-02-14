from __future__ import annotations


class Data:
    """
    A class to store a value and its corresponding time. Calculation with ``+``, ``-``, ``*``, ``/`` and all types of
    comparisons can be applied directly to the class.

    :param value: the value that should be stored
    :type value: float

    :param time: the corresponding time to the value
    :type time: float
    """
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
    """
    A class to extend the :class:`Data <.Data>`. This class stores velocity values and the
    acceleration can be easily calculated
    """
    def __str__(self):
        return f"{self.value} m/s @ {self.time} s"

    @property
    def speed(self):
        return self.value

    def acceleration(self, other: Speed) -> Data:
        """
        A method to calculate the acceleration

        :param other: the Speed before with which the Acceleration should be calculated
        :return: the Acceleration
        :rtype: Data
        """
        delta_t = (self.time - other.time)
        if delta_t == 0:
            return Speed(0, 0)
        return Data(self.value / (self.time - other.time), self.time)


class Distance(Data):
    """
    A class to extend the :class:`Data <.Data>`. This class stores distance values and the
    velocity can be easily calculated
    """
    def __str__(self):
        return f"{self.value} m @ {self.time} s"

    @property
    def distance(self):
        return self.value

    def velocity(self, other: Distance) -> Speed:
        """
        A method to calculate the velocity. Returns Speed with value 1 if the times are the same

        :param other: the Distance before with which the speed should be calculated
        :return: the speed
        :rtype: Speed
        """
        try:
            return Speed((other.value - self.value) / (self.time - other.time), self.time)
        except ZeroDivisionError:
            return Speed(1, self.time)