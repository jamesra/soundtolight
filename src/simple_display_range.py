import ema
import ulab.numpy as np

class SimpleDisplayRange:
    '''
    Tracks inputs and attempts to choose a reasonable normalization for groups of numbers over time
    '''

    def __init__(self, num_groups):
        self.num_groups = num_groups
        self.last_max_total_power = 0
        self.last_min_total_power = 1 << 15
        #self._mean_group_power_ema = []
        self.max_individual_group_power = None
        self.groups_max_power = None
        self.groups_min_power = None

        self._ema_total_power = ema.EMA(500, 1.2)

        #for i in range(0, num_groups):
            #self._mean_group_power_ema.append(ema.EMA(500, 1.5))

    def add(self, group: np.array):
        '''
        There is some magic here.  The device exists in an environment with variable amount of noise.  We want the
        display to be relative to the ambient noise level.  So we track the min/max values, but have them slowly
        decay to the mean power level.  We also use the current group power to adjust the min/max if they exceed
        the current min/max values.
        '''
        if len(group) != self.num_groups:
            raise ValueError("Expected group length to match num_groups")
        #print(f'group: {group}')

        group = group ** 1.5

        #self.last_min_total_power = 200
        #self.last_max_total_power = 20000

        if self.groups_max_power is None:
            self.groups_max_power = group

        if self.groups_min_power is None:
            self.groups_min_power = group

        #print(np.ndarray((group, self.groups_max_power)))
        self.groups_max_power = np.max(np.ndarray((group, self.groups_max_power * 0.999)), axis=0)
        self.groups_min_power = np.min(np.ndarray((group, self.groups_min_power)), axis=0)

        #self.groups_min_power_log = np.log(self.groups_min_power)
        #self.groups_max_power_log = np.log(self.groups_max_power)

        # total_power = np.sum(group)
        #self.groups_max_power = np.max([(self.groups_max_power), (group)], axis=1)
        #print(f'min group power: {self.groups_min_power}')
        #print(f'max group power: {self.groups_max_power}')

        #print(f'Scaled EMA Total: {self.scaled_total_power}')
        #print(f'min: {min_power} max: {max_power} scaled_total_power: {self.scaled_total_power}')



        #print(f'Normalized power: {self.groups_normalized}')

    def get_normalized_values(self, group_power: np.array[float]):

        if self.groups_min_power is None:
            return None

        group_power = group_power ** 1.5

        #group_log_power = np.log(group_power)

        # print(f'gp: {group_power}\nmigp:{self.max_individual_group_power}\nstp:{self.scaled_total_power}')
        #group_power = group_power / self._ema_total_power.ema_value
        #result = (group_power / self.max_individual_group_power) * self.scaled_total_power
        result = (group_power - self.groups_min_power) / self.groups_max_power

        #result = (group_log_power - (self.groups_min_power_log * 1.05)) / (self.groups_max_power_log * .95)

        result[result > 1] = 1.0
        result[result < 0] = 0
        return result

    def get_normalized_value(self, igroup, value):

        if self.max_individual_group_power is None:
            return None

        #value = value / self._ema_total_power.ema_value
        #return (value / self.max_individual_group_power) * self.scaled_total_power