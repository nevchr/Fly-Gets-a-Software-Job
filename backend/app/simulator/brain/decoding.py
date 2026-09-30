"""Deterministic decoding of real descending-neuron spike activity."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


BINARY_POPULATIONS = (
    ("false / avoid", ("steer_R",)),
    ("true / approach", ("steer_L",)),
)
OPTION_POPULATIONS = (
    ("option 0 / steer left", ("steer_L",)),
    ("option 1 / steer right", ("steer_R",)),
    ("option 2 / escape", ("escape_L", "escape_R")),
    ("option 3 / forward", ("forward_L", "forward_R")),
    ("option 4 / backward", ("backward_L", "backward_R")),
    ("option 5 / courtship song", ("kick_L", "kick_R")),
)


@dataclass(frozen=True)
class DecodedAction:
    index: int
    label: str
    scores: tuple[dict[str, float | int | bool], ...]


class ActionDecoder:
    def __init__(self, brain):
        self.brain = brain

    def _indices(self, group_names: tuple[str, ...]) -> np.ndarray:
        arrays = [np.asarray(self.brain.groups[name], dtype=np.int64) for name in group_names]
        return np.unique(np.concatenate(arrays))

    def population_mapping(self, option_count: int | None = None) -> tuple:
        if option_count is None:
            return BINARY_POPULATIONS
        if not 1 <= option_count <= len(OPTION_POPULATIONS):
            raise ValueError(f"connectome decoder supports 1-{len(OPTION_POPULATIONS)} options")
        return OPTION_POPULATIONS[:option_count]

    def decode(
        self,
        spike_counts: np.ndarray,
        duration_seconds: float,
        option_count: int | None = None,
    ) -> DecodedAction:
        scores = []
        for label, group_names in self.population_mapping(option_count):
            indices = self._indices(group_names)
            spikes = int(spike_counts[indices].sum())
            scores.append({
                "name": label,
                "spike_rate": float(spikes / max(len(indices) * duration_seconds, 1e-9)),
                "spikes": spikes,
                "neurons": int(len(indices)),
                "selected": False,
            })
        selected = int(np.argmax([score["spike_rate"] for score in scores]))
        scores[selected]["selected"] = True
        return DecodedAction(selected, str(scores[selected]["name"]), tuple(scores))
