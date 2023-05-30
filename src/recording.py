import math
import ulab.numpy as np
import recording_settings

def get_frequencies(settings: recording_settings.RecordingSettings):
    '''
    Determine the frequency for each bin of an FFT performed with a
    recording sample with the provided settings
    :param settings:
    :return:
    '''
    frequency_bin_width = settings.sample_rate / settings.sample_size
    frequencies = np.arange(0, (frequency_bin_width * settings.sample_size) / 2.0, frequency_bin_width)
    print(f"bin width: {frequency_bin_width} n_samples: {settings.sample_size}\nfrequencies: {frequencies}")
    return frequencies

def get_frequency_index(frequencies: np.array,  value: float):
    '''
    This is a brute-force search for last index equal to or below the requested frequency
    :param frequencies:
    :param freq:
    :return:
    '''
    max_freq_index = 0
    for i, freq in enumerate(frequencies):
        if freq > value:
            break

        max_freq_index = i

    return max_freq_index

def calculate_hamming_filter(length: int) -> np.array[float]:
    range = math.pi / 2.0
    bin_width = range / length
    filter = np.array([math.sin(x) for x in np.arange(0, range, bin_width)])
    print(f'Hamming filter, len {length}: {filter}')
    return filter


def get_cutoff_frequency_index(settings: recording_settings.RecordingSettings):
    '''
    This is a brute-force search for the index of the cutoff frequency for a RecordingSettings object
    :param frequencies:
    :param freq:
    :return:
    '''
    frequencies = get_cutoff_frequency_index(settings)
    return get_frequency_index(frequencies, settings.frequency_cutoff)