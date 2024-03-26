import math
import ulab.numpy as np
import neopixel
from spectrum_shared import map_float_color_to_neopixel_color, \
    map_power_to_range, map_normalized_value_to_color, log_range, float_to_indicies, get_freq_powers_by_range, \
    linear_range, space_indicies, map_normalized_power_to_range
from interfaces import IDisplay
from display_settings import DisplaySettings
import colormap
from standard_colormaps import default_colormap
import display_range
import simple_display_range

class BasicDisplay(IDisplay):
    last_min_group_power: float
    last_max_group_power: float
    pixels: neopixel.NeoPixel
    num_groups: int  # How many groups we display, defaults to number of pixels
    num_cutoff_groups: int  # How many low frequency groups we ignore
    _log_range_indicies: np.array[int]
    _group_power: np.array[float]
    settings: DisplaySettings

    @property
    def num_visible_groups(self) -> int:
        return self.num_cols * self.num_rows

    @property
    def num_cols(self) -> int:
        return self.settings.num_cols

    @property
    def num_rows(self) -> int:
        return self.settings.num_rows

    @property
    def pixel_indexer(self):
        return self.settings.indexer

    @property
    def total_groups(self) -> int:
        return self.num_groups + self.num_cutoff_groups

    def __init__(self, pixels: neopixel.NeoPixel, settings: DisplaySettings, num_cutoff_groups: int = 0, cmap: colormap.ColorMap | None = None):
        self.pixels = pixels
        self.settings = settings
        self._display_range = simple_display_range.SimpleDisplayRange(settings.num_cols * settings.num_rows)
        self.num_cutoff_groups = num_cutoff_groups
        self._group_power = None
        self._colormap = cmap if cmap is not None else default_colormap

        self._range_indicies = None
        self._pixel_map = self._build_pixel_map()

    def _build_pixel_map(self):
        '''
        Create a map to index column first, row second to optimize access
        '''
        col_map = [tuple()] * self.num_cols
        for i_col in range(0, self.num_cols):
            row_map = []
            i_shift_col = i_col + (self.num_cols // 2)
            if i_shift_col >= self.num_cols:
                i_shift_col -= self.num_cols

            #print(f'i_shift_col: {i_shift_col}')

            for i_row in range(0, self.num_rows):
                i_target = self.pixel_indexer(i_row, i_col, self.settings)
                row_map.append(i_target)
            col_map[i_shift_col] = tuple(row_map)

        return tuple(col_map)

    def _build_range_indicies(self, spectrum_len):
        '''
        Figure out if we need to squeeze frequencies together to fit in a single pixel
        :param spectrum_len:
        :return:
        '''
        if self.settings.log_scale:
            range = log_range(spectrum_len, self.num_visible_groups)
        else:
            range = linear_range(spectrum_len, self.num_visible_groups)

        range_indicies = float_to_indicies(range)
        range_indicies = space_indicies(range_indicies)
        return range_indicies

    def show(self, power_spectrum):
        if self._range_indicies is None:
            self._range_indicies = self._build_range_indicies(len(power_spectrum))

        self._group_power = get_freq_powers_by_range(power_spectrum,
                                                     self._range_indicies,
                                                     out=self._group_power)



        norm_values = self._display_range.get_normalized_values(self._group_power)
        #print(f'{norm_values}')
        if norm_values is None:
            self._display_range.add(self._group_power)
            return

        #print(f'{norm_values}')

        for i_row in range(self.num_rows):
            row_offset = i_row * self.num_cols
            for i_col in range(self.num_cols):
                iPixel = self._pixel_map[i_col][i_row]
                i = row_offset + i_col

                norm_value = norm_values[i]
                if norm_value is None:
                    self.pixels[iPixel] = (0, 0, 0)
                    continue

                i_range, norm_value = map_normalized_power_to_range(norm_value,
                                                                    range_cutoffs=self._colormap.range_cutoffs)
                if norm_value < 0 or norm_value > 1.0:
                    raise ValueError(f'norm_value {norm_value}')

                neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range,
                                                          color_map=self._colormap.colors)

                #print(f'{i}: nv: {norm_value} color: {neo_color}')
                self.pixels[iPixel] = map_float_color_to_neopixel_color(neo_color, norm_value)

        self.pixels.show()

        self._display_range.add(self._group_power)