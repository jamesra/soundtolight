import ema


class PixelEMA:
    '''
    Accumulates values over time, calculating an exponential moving average over time
    '''

    _R: ema.EMA
    _G: ema.EMA
    _B: ema.EMA

    def __init__(self, num_samples: int, smooth: float = 2):
        self._R = ema.EMA(num_samples, smooth)
        self._G = ema.EMA(num_samples, smooth)
        self._B = ema.EMA(num_samples, smooth)

    @property
    def ema_value(self) -> tuple[float, float, float]:
        return self._R.ema_value, self._G.ema_value, self._B.ema_value

    def add(self, value: tuple[float, float, float]):
        #print(f'add {value}')
        self._R.add(value[0])
        self._G.add(value[1])
        self._B.add(value[2])
