import random

from app.simulator.brain.base import BrainActivity, BrainAdapter, BrainContext


class MockBrainAdapter(BrainAdapter):
    """Seeded stand-in for a future connectome-backed adapter."""

    def __init__(self, seed: int = 314159):
        self._random = random.Random(seed)
        self._decision_count = 0
        self._last_activation = 0.5
        self._spikes = [0.0] * 18

    def _pulse(self) -> float:
        self._decision_count += 1
        self._last_activation = self._random.random()
        self._spikes = self._spikes[1:] + [self._last_activation]
        return self._last_activation

    def choose_binary(self, context: BrainContext) -> bool:
        threshold = float(context.signals.get("threshold", 0.5))
        return self._pulse() >= max(0.0, min(1.0, threshold))

    def choose_option(self, context: BrainContext, options: list[str]) -> int:
        if not options:
            raise ValueError("Brain cannot choose from an empty option list")
        self._pulse()
        return self._random.randrange(len(options))

    def get_activity_snapshot(self) -> BrainActivity:
        activation = self._last_activation
        regions = ["mushroom body", "optic lobe", "central complex", "panic circuit"]
        return BrainActivity(
            activation=activation,
            firing_rate=18 + activation * 94,
            dominant_region=regions[self._decision_count % len(regions)],
            spikes=list(self._spikes),
            decision_count=self._decision_count,
            backend="mock",
            device="seeded-python",
            mean_activity=activation,
            spike_rate=18 + activation * 94,
        )

    @property
    def backend_name(self) -> str:
        return "mock"
