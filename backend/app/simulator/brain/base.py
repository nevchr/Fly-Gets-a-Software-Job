from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BrainContext:
    decision: str
    stage: str
    signals: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BrainActivity:
    activation: float
    firing_rate: float
    dominant_region: str
    spikes: list[float]
    decision_count: int
    backend: str = "mock"
    dataset: str | None = None
    neuron_count: int = 0
    connection_count: int = 0
    device: str = "cpu"
    mean_activity: float = 0.0
    active_neurons: int = 0
    spike_rate: float = 0.0
    input_activity: list[dict[str, Any]] = field(default_factory=list)
    output_activity: list[dict[str, Any]] = field(default_factory=list)
    sampled_neurons: list[int] = field(default_factory=list)
    visual_neurons: list[dict[str, Any]] = field(default_factory=list)
    decision_latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BrainAdapter(ABC):
    """The only decision-making surface the simulator is allowed to use."""

    @abstractmethod
    def choose_binary(self, context: BrainContext) -> bool:
        raise NotImplementedError

    @abstractmethod
    def choose_option(self, context: BrainContext, options: list[str]) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_activity_snapshot(self) -> BrainActivity:
        raise NotImplementedError

    @property
    def backend_name(self) -> str:
        return "unknown"
