try:
    import ulab.numpy as np
except ModuleNotFoundError:
    import numpy as np

class ColorMap:
    @property
    def range_cutoffs(self):
        return self._range_cutoffs

    @property
    def range_deltas(self):
        return self._range_deltas

    @property
    def colors(self):
        return self._colors

    def __init__(self, colors: list[tuple[float, float, float]], ranges: list[float] | None):
        if len(ranges) != len(colors):
            raise ValueError("Number of range entries must match number of color entries")


        self._colors = colors

        #Evenly space the colors if not provided a range
        self._range_cutoffs = np.array(ranges if ranges is not None else np.arange(1, len(colors) + 1) / (len(colors) + 1))

        self._range_deltas = [self._range_cutoffs[i] - self._range_cutoffs[i-1] for i in range(1, len(self._range_cutoffs))]
        self._range_deltas.insert(0, self._range_cutoffs[0])
        #print(f'{self._range_deltas}')