import ema
import ulab.numpy as np

class DisplayRange:
    '''
    Tracks inputs and attempts to choose a reasonable normalization for groups of numbers over time
    '''

    def __init__(self, num_groups):
        self.num_groups = num_groups
        self.last_max_total_power = 0
        self.last_min_total_power = 1 << 15
        self._mean_group_power_ema = []
        self.groups_normalized = None
        self.max_individual_group_power = None


        self._ema_total_power = ema.EMA(500, 1.1)

        for i in range(0, num_groups):
            self._mean_group_power_ema.append(ema.EMA(500, 1.5))

    def add(self, group):
        '''
        There is some magic here.  The device exists in an environment with variable amount of noise.  We want the
        display to be relative to the ambient noise level.  So we track the min/max values, but have them slowly
        decay to the mean power level.  We also use the current group power to adjust the min/max if they exceed
        the current min/max values.
        '''
        if len(group) != self.num_groups:
            raise ValueError("Expected group length to match num_groups")

        total_power = np.sum(group)
        self.groups_normalized = group / total_power
        self.max_individual_group_power = np.max(self.groups_normalized)
        self.groups_normalized /= self.max_individual_group_power

        self._ema_total_power.add(total_power)

        #self.scaled_total_power = (total_power / self._ema_total_power.ema_value)
        #print(f'EMA Total Power: {self.ema_total_power.ema_value} total: {total_power}')
        self.last_min_total_power = min(self.last_min_total_power * 1.0005, total_power,
                                        self._ema_total_power.ema_value)  # Slowly decay min/max
        self.last_max_total_power = max(self.last_max_total_power * .999, total_power,
                                        self._ema_total_power.ema_value)
        #
        #
        min_power = self.last_min_total_power
        max_power = self.last_max_total_power
        #
        scaled_power_range = max_power - min_power
        #
        if scaled_power_range != 0:
            self.scaled_total_power = (total_power - min_power) / scaled_power_range
        else:
            self.scaled_total_power = total_power / self._ema_total_power.ema_value

        #print(f'Scaled EMA Total: {self.scaled_total_power}')



        #print(f'Normalized power: {self.groups_normalized}')

    def get_normalized_value(self, igroup, value):

        if self.groups_normalized is None:
            return None

        return self.groups_normalized[igroup] * self.scaled_total_power
