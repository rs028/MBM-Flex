from typing import List, Tuple


class TimeDependentValue:
    """
        @brief A class recording a variable which varies in time
        Stored in the form of a list of tuples,
        each  tuple has a time and a value 
        it can be continuous which means that linear interpolation will be performed between defined times

    """

    def __init__(self, values: List[Tuple[float, float]], continuous):

        if len(values) == 0:
            raise Exception("no times provided")

        for i in range(len(values)-1):
            if (values[i][0] >= values[i+1][0]):
                raise Exception("times were not in order")

        self._values: List[Tuple[float, float]] = values
        self._continuous = continuous

    def times(self) -> List[float]:
        return [v[0] for v in self._values]

    def values(self) -> List[float]:
        return [v[1] for v in self._values]

    def value_at_time(self, t: float) -> float:
        """
        Returns the value at time t using linear interpolation.
        """
        if t < self._values[0][0]:
            raise Exception("Time is too early")

        if t > self._values[-1][0]:
            raise Exception("Time is too late")

        # Compare with the exact times
        for t0, v0 in self._values:
            if t == t0:
                return v0

        # Linear interpolation if between 2 times
        for i in range(len(self._values) - 1):
            t0, v0 = self._values[i]
            t1, v1 = self._values[i + 1]

            if t0 <= t <= t1:
                if(self._continuous):
                    return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
                else:
                    return v0

        raise Exception("Invalid time")
