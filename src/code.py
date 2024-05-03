# This is a sample Python script.
import time
import math

import asyncio
import board
import analogbufio
import array
import ulab.numpy as np
import neopixel
import digitalio
from collections import namedtuple

import ulab.utils
import ema
import display_diagnostic
from recording_settings import RecordingSettings
import recording
from sound_rec import record_sample_array, record_sample_numpy
from basic_display import BasicDisplay
from waterfall_display import WaterfallDisplay
from graph_display import GraphDisplay
from fade_display import FadeDisplay
from display_settings import DisplaySettings
from pixel_indexers import *

import adafruit_dotstar as dotstar
from colormap import ColorMap
import standard_colormaps

# Known display configurations.
display_configs = {
    "32x8 Waterfall": DisplaySettings(num_rows=32, num_cols=8,
                                      pixel_indexer=columns_are_rows_with_alternating_column_order_indexer,
                                      log_scale=False),
    "8x32 Graph": DisplaySettings(num_rows=8, num_cols=32,
                                  pixel_indexer=rows_are_columns_with_alternating_reversed_column_order_indexer,
                                  log_scale=False),
    "8x4 Neopixel Feather Graph": DisplaySettings(num_rows=4, num_cols=8, pixel_indexer=flip_column_order_indexer,
                                                  log_scale=True),
    "8x4 Neopixel Feather Waterfall": DisplaySettings(num_rows=4, num_cols=8, pixel_indexer=flip_column_order_indexer,
                                                      log_scale=True),
    "4x16 Graph": DisplaySettings(num_rows=8, num_cols=32,
                                  pixel_indexer=rows_are_columns_with_alternating_reversed_column_order_indexer,
                                  num_neo_rows=8, num_neo_cols=32,
                                  log_scale=True),
    "6x12 Dotstar Feather Graph": DisplaySettings(num_rows=6, num_cols=12, pixel_indexer=standard_indexer,
                                                  log_scale=True),
    "12x6 Dotstar Feather Waterfall": DisplaySettings(num_rows=12, num_cols=6, pixel_indexer=rows_are_columns_indexer,
                                                      log_scale=True),
    "6x12 Dotstar Feather Waterfall": DisplaySettings(num_rows=6, num_cols=12, pixel_indexer=standard_indexer,
                                                      log_scale=True),
}

# The Electet Microphone used in this project can only sample at up to 20Khz according to its specs.  Higher values just add noise.
sampling_settings = {
    "Low Frequency": RecordingSettings(sampling_freq_hz=20000, frequency_cutoff=255, sample_size_exp=10),
    "Low-Mid Frequency": RecordingSettings(sampling_freq_hz=20000, frequency_cutoff=500, sample_size_exp=10),
    "Mids": RecordingSettings(sampling_freq_hz=20000, frequency_cutoff=4000, sample_size_exp=10),
    "High-Mids": RecordingSettings(sampling_freq_hz=20000, frequency_cutoff=6000, sample_size_exp=10),
    "Highs": RecordingSettings(sampling_freq_hz=20000, frequency_cutoff=10000, sample_size_exp=10),
}

sample_settings = sampling_settings["Mids"]

MIC_PIN = board.A5

purple_colormap = ColorMap(standard_colormaps.purple_colors, standard_colormaps.default_graph_cutoffs)
purple_basic_colormap = ColorMap(standard_colormaps.purple_colors, standard_colormaps.default_basic_cutoffs)
green_colormap = ColorMap(standard_colormaps.green_colors, standard_colormaps.default_graph_cutoffs)
red_colormap = ColorMap(standard_colormaps.red_colors, standard_colormaps.default_graph_cutoffs)
rainbow_colormap = ColorMap(standard_colormaps.default_colors, standard_colormaps.default_graph_cutoffs)
rainbow_basic_colormap = ColorMap(standard_colormaps.default_colors, standard_colormaps.default_basic_cutoffs)



class NeoPixelFeatherWing:
    @property
    def display_modes(self):
        return self._display_modes

    def __init__(self):
        NeoPixelFeatherWing._pixels = neopixel.NeoPixel(board.D6, n=4 * 8, brightness=0.05, auto_write=False)
        self._display_modes = (
            GraphDisplay(NeoPixelFeatherWing._pixels, display_configs["8x4 Neopixel Feather Graph"],
                         cmap=green_colormap),
            WaterfallDisplay(NeoPixelFeatherWing._pixels, display_configs["8x4 Neopixel Feather Waterfall"]),
            FadeDisplay(NeoPixelFeatherWing._pixels, display_configs["8x4 Neopixel Feather Graph"],
                        cmap=purple_colormap, smooth_factor=2.66, smooth_samples=3),
            BasicDisplay(NeoPixelFeatherWing._pixels, display_configs["8x4 Neopixel Feather Graph"],
                         cmap=rainbow_colormap),
        )


class NeoPixel32x8Matrix:
    @property
    def display_modes(self):
        return self._display_modes

    def __init__(self):
        NeoPixel32x8Matrix._pixels = neopixel.NeoPixel(board.D10, n=8 * 32, brightness=0.05, auto_write=False)
        self._display_modes = (
            GraphDisplay(NeoPixel32x8Matrix._pixels, display_configs["8x32 Graph"], cmap=green_colormap),
            WaterfallDisplay(NeoPixel32x8Matrix._pixels, display_configs["32x8 Waterfall"]),
            FadeDisplay(NeoPixel32x8Matrix._pixels, display_configs["8x32 Graph"], cmap=purple_colormap,
                        smooth_factor=2.66,
                        smooth_samples=3),
        )


class DotStarFeatherWing:
    @property
    def display_modes(self):
        return self._display_modes

    def __init__(self):
        DotStarFeatherWing._dotstar = dotstar.DotStar(board.D13, board.D11, 12 * 6, brightness=.1, auto_write=False)
        self._display_modes = (
            GraphDisplay(DotStarFeatherWing._dotstar, display_configs["6x12 Dotstar Feather Graph"],
                         cmap=green_colormap),
            FadeDisplay(DotStarFeatherWing._dotstar, display_configs["6x12 Dotstar Feather Graph"],
                        cmap=red_colormap,
                        smooth_factor=2.5, smooth_samples=4),
            WaterfallDisplay(DotStarFeatherWing._dotstar, display_configs["12x6 Dotstar Feather Waterfall"]),
            WaterfallDisplay(DotStarFeatherWing._dotstar, display_configs["6x12 Dotstar Feather Waterfall"]),
            WaterfallDisplay(DotStarFeatherWing._dotstar, display_configs["6x12 Dotstar Feather Waterfall"], cmap=green_colormap),
            BasicDisplay(DotStarFeatherWing._dotstar, display_configs["6x12 Dotstar Feather Graph"],
                         cmap=rainbow_colormap),
            BasicDisplay(DotStarFeatherWing._dotstar, display_configs["6x12 Dotstar Feather Graph"],
                         cmap=purple_basic_colormap),
        )


# On-board DotStar for boards including Gemma, Trinket, and ItsyBitsy
display = DotStarFeatherWing()
#display = NeoPixelFeatherWing()
# display = NeoPixel32x8Matrix()
display_modes = display.display_modes
iDisplayMode = 0
display_mode = display_modes[iDisplayMode]


# btn_pin = digitalio.DigitalInOut(board.D12)
# btn_pin.switch_to_input(digitalio.Pull.DOWN)

def OnModeButtonDown():
    global iDisplayMode
    global display_mode
    iDisplayMode += 1
    if iDisplayMode >= len(display_modes):
        iDisplayMode = 0

    display_mode = display_modes[iDisplayMode]


#####################################################################

ButtonConfig = namedtuple("ButtonConfig", ('pin', 'on_down_func'))

buttons = (
    ButtonConfig(digitalio.DigitalInOut(board.D12), OnModeButtonDown),
)

#####################################################################

for i, button in enumerate(buttons):
    button.pin.switch_to_input(digitalio.Pull.DOWN)


async def Run():
    global display_mode
    global buttons

    buttons_last_state = [False] * len(buttons)
    #######################################################
    # Use reversing_row_column_indexer if your NeoPixels
    # initialize going back and forth like mowing the lawn.
    # Use None if your neopixel rows initalize in one
    # direction
    # row_indexer=reversing_row_column_indexer
    ########################################

    # display_mode = display_modes[iDisplayMode]

    #######################################################
    # If you have a new display_mode the functions below can
    # help determine pixel order and if a pixel indexer
    # is addressing the pixels correctly
    #######################################################
    # display_diagnostic.ShowLightOrder(display_mode.pixels, display_mode.settings, 0.01)
    # display_diagnostic.ShowRowColumnOrder(display_mode.pixels, display_mode.settings, 0.01)
    #######################################################

    # Initialize a region of memory to read microphone data into
    mic_buffer = array.array("H", [0x0000] * sample_settings.sample_size)

    # analogbufio makes calls external to python to allow reading the microphone fast enough to encode high frequencies
    mic_adc_bufferio = analogbufio.BufferedIn(MIC_PIN, sample_rate=sample_settings.sample_rate)

    # async tasks are a way to simplify concurrency (doing more than one set of operations).  We are asking python to
    # read data into the microphone as a separate task from this task which is processing the sound.
    # (Currently circuitpython is not able to run both tasks simultaneously, but hopefully tasks will be improved in
    # later versions and doing it "right" means this code will improve if better task concurrency makes it into circuit
    # python.)

    # Get a big sample to calculate a mean buffer value
    new_buffer_task = asyncio.create_task(
        record_sample_array(mic_adc_bufferio, sample_settings.sample_size * 10, sample_rate=sample_settings.sample_rate,
                            buffer=mic_buffer))

    # The max_buffer_ema is used to normalize the recorded signal.  An exponential moving average (EMA) is used to slowly
    # adjust the volume range that the microphone is focusing on.  A large number of samples in the EMA means the value
    # will adapt slowly to changes in sound.  Smaller number of samples may adjust the range based on quiet stretces of
    # music or conversations and then saturate the diaplay when the volume increases.
    # The smooth factor determines how much weight is given to the more recent records.  A typical value is 2, but again
    # the default is 1.5 to prevent the display_mode from adapting too quickly to music that has long loud/quiet periods at
    # the cost of adapting slowly if the overall volume changes for a long period of time (example: changing the volume
    # knob on the speaker.)
    max_buffer_ema = ema.EMA(num_samples=500, smooth=1)

    # The best results I obtained experimenting with this code was to have a high sampling rate (~22,000 Hertz) and then
    # eliminating high frequencies from the data.  This seems counter-intuitive, why collect the high frequencies if
    # we just throw them away?  The reason is I use a log axis for several displays.  This means more columns are devoted
    # to the low frequency information than the high frequency information.  The extra resolution in the low range from
    # a large number of samples
    # The FFT we run will give us one measurement for every sample we collect.  We want a lot of low frequency
    # information because that is where the human voice (85Hz to 255Hz)  and a lot of musical notes are.  However people can hear up
    # to about 22,000Hz and some music uses much higher frequencies.

    # The ESP32-S3 this program originally runs on can only process 1024 samples with an FFT fast enough to have a
    # decent refresh rate. That produces information for 512 frequencies (the other 512 are essentially a mirror image
    # of the first.  Wikipedia or another resource can explain in more depth why that is.)
    frequencies = recording.get_frequencies(sample_settings)
    max_freq_index = recording.get_frequency_index(frequencies, sample_settings.frequency_cutoff)
    print(f'max freq index: {max_freq_index}')

    # filter_len = sample_settings.sample_size >> 1 # This is a fancy divide by 2 that ensures we still have an integer
    # hanning_filter = recording.calculate_half_hanning_filter(filter_len)
    # print(f'Hanning filter, len {filter_len}: {hanning_filter}')
    # reversed_hanning_filter = hanning_filter[::-1]
    # print(f'Reverse filter: {reversed_hanning_filter}')

    hanning_filter = recording.calculate_hanning_filter(sample_settings.sample_size)
    print(f'Hanning filter, len {len(hanning_filter)}: {hanning_filter}')

    # Collect the first sample so we can precalculate the signal mean
    sample_buffer = np.array(await new_buffer_task)

    max_buffer_ema.add(np.max(sample_buffer))
    buffer_mean = int(round(np.mean(sample_buffer)))

    print(f'Mean buffer value calculated as {buffer_mean}')

    while True:
        ###################
        # Sample Collection
        ###################
        # print(btn_pin.value)

        for i, button in enumerate(buttons):
            btn_state = button.pin.value
            btn_change = buttons_last_state[i] != btn_state
            if btn_change and btn_state is True:
                button.on_down_func()
            buttons_last_state[i] = btn_state

        # Wait for the audio sample to finish collecting
        mic_buffer = await new_buffer_task

        # Start a task to collect the audio sample
        new_buffer_task = asyncio.create_task(
            record_sample_array(mic_adc_bufferio, sample_settings.sample_size, sample_rate=sample_settings.sample_rate,
                                buffer=mic_buffer))

        #########################
        # Process the audio sample
        #########################

        # Convert to a numpy.array
        sample_buffer = np.array(mic_buffer, dtype=np.float)

        # buffer_mean = int(round(np.mean(sample_buffer)))
        # print(f'Mean buffer value calculated as {buffer_mean}')
      # Center the floating point sample buffer so the value of 0 represents no sound
        sample_buffer -= buffer_mean
        max_buffer_ema.add(np.max((sample_buffer)))  # Technically should call abs here, but odds are this is close enough

        sample_buffer /= max_buffer_ema.ema_value
        #print(f'Max buffer EMA: {max_buffer_ema.ema_value}')

        # Filter the window to reduce spectral leakage
        sample_buffer *= hanning_filter

        # Calculate the FFT (determine which frequencies compose the recording)
        power_spectrum = ulab.utils.spectrogram(sample_buffer)

        # Remove half of the FFT, which is mostly symmetric for this data
        displayed_power_spectrum = power_spectrum[1:max_freq_index]

        # Show the FFT with our chosen display_mode
        display_mode.show(displayed_power_spectrum)
        # time.sleep(0.5)


asyncio.run(Run())
