import numpy as np

from app.simulator.brain.decoding import ActionDecoder


class FakeBrain:
    groups = {
        "steer_L": np.array([0]),
        "steer_R": np.array([1]),
        "escape_L": np.array([2]),
        "escape_R": np.array([3]),
        "forward_L": np.array([4]),
        "forward_R": np.array([5]),
        "backward_L": np.array([6, 7]),
        "backward_R": np.array([8, 9]),
        "kick_L": np.array([10]),
        "kick_R": np.array([11]),
    }


def test_binary_decoding_compares_symmetric_steering_populations():
    counts = np.zeros(12, dtype=np.int32)
    counts[0] = 3
    result = ActionDecoder(FakeBrain()).decode(counts, duration_seconds=0.25)
    assert result.index == 1
    assert result.label == "true / approach"


def test_option_decoding_maps_distinct_populations_and_ties_lowest():
    decoder = ActionDecoder(FakeBrain())
    assert len(decoder.population_mapping(6)) == 6
    tied = decoder.decode(np.zeros(12, dtype=np.int32), 0.25, option_count=6)
    assert tied.index == 0

    counts = np.zeros(12, dtype=np.int32)
    counts[2] = counts[3] = 4
    escape = decoder.decode(counts, 0.25, option_count=4)
    assert escape.index == 2

