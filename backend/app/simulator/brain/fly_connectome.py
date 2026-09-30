"""Real MaleCNS v1.0 connectome-backed BrainAdapter."""

from __future__ import annotations

import logging
import math
import threading
import time
from collections import deque
from pathlib import Path

import numpy as np

from app.simulator.brain.base import BrainActivity, BrainAdapter, BrainContext
from app.simulator.brain.decoding import ActionDecoder
from app.simulator.brain.encoding import EncodedStimulus, SensoryEncoder


LOGGER = logging.getLogger("uvicorn.error")
EXPECTED_NEURONS = 166_700
EXPECTED_CONNECTIONS = 25_582_938
DATASET_NAME = "MaleCNS v1.0"
VISUAL_BODY_IDS = (10573, 21065, 16128, 14465, 12052, 523769, 10360)


class FlyConnectomeAdapter(BrainAdapter):
    """One continuing flybrain.FlyBrain instance for the process lifetime."""

    def __init__(
        self,
        seed: int = 314159,
        device: str = "auto",
        decision_ms: int = 250,
        data_dir: str | Path | None = None,
    ):
        try:
            import flybrain
        except ImportError as error:
            raise RuntimeError(
                "Connectome mode requires flybrain. Run: pip install flybrain"
            ) from error

        resolved_data = Path(data_dir).expanduser() if data_dir else Path(flybrain.DATA)
        if not flybrain.has_data(resolved_data):
            raise RuntimeError(
                f"MaleCNS brain data is missing from {resolved_data}. "
                f'Run: flybrain download --data "{resolved_data}"'
            )

        started = time.perf_counter()
        self._brain = flybrain.FlyBrain(data=resolved_data, seed=seed, device=device)
        self._encoder = SensoryEncoder()
        self._decoder = ActionDecoder(self._brain)
        self._lock = threading.RLock()
        self._population_cache: dict[tuple[tuple[str, ...], str], np.ndarray] = {}
        self._decision_count = 0
        self._decision_ms = int(decision_ms)
        self._step_count = max(1, math.ceil(self._decision_ms / (self._brain.dt * 1000)))
        self._latencies: deque[float] = deque(maxlen=100)
        self._package_version = flybrain.__version__
        self._data_dir = resolved_data
        self._connection_count = int(len(self._brain.weights))
        if self._brain.n != EXPECTED_NEURONS or self._connection_count != EXPECTED_CONNECTIONS:
            raise RuntimeError(
                "Unexpected flybrain dataset: "
                f"{self._brain.n} neurons/{self._connection_count} connections; "
                f"expected {EXPECTED_NEURONS}/{EXPECTED_CONNECTIONS} for {DATASET_NAME}."
            )
        with np.load(resolved_data / "brain.npz") as metadata:
            body_ids = metadata["ids"]
        self._visual_indices = {}
        for body_id in VISUAL_BODY_IDS:
            index = int(np.searchsorted(body_ids, body_id))
            if index >= len(body_ids) or body_ids[index] != body_id:
                raise RuntimeError(f"Missing visual neuron body ID: {body_id}")
            self._visual_indices[body_id] = index

        # Trigger CPU kernel compilation at startup rather than on the first
        # career decision. This advances the same continuing neural state once.
        self._brain.step()
        self.initialization_seconds = time.perf_counter() - started
        self._last = BrainActivity(
            activation=0.0,
            firing_rate=0.0,
            dominant_region="awaiting sensory input",
            spikes=[0.0] * self._step_count,
            decision_count=0,
            backend="connectome",
            dataset=DATASET_NAME,
            neuron_count=self._brain.n,
            connection_count=self._connection_count,
            device=self._brain.device,
            visual_neurons=[{"body_id": body_id, "spike_count": 0, "spike_rate": 0.0}
                            for body_id in VISUAL_BODY_IDS],
        )
        LOGGER.info(
            "Fly brain initialized | backend=%s | package=%s | neurons=%s | connections=%s | device=%s | init=%.3fs",
            DATASET_NAME,
            self._package_version,
            self._brain.n,
            self._connection_count,
            self._brain.device,
            self.initialization_seconds,
        )

    @property
    def backend_name(self) -> str:
        return "connectome"

    @property
    def metadata(self) -> dict:
        return {
            "backend": self.backend_name,
            "dataset": DATASET_NAME,
            "package": "flybrain",
            "package_version": self._package_version,
            "neurons": self._brain.n,
            "connections": self._connection_count,
            "device": self._brain.device,
            "data_dir": str(self._data_dir),
            "decision_ms_requested": self._decision_ms,
            "decision_ms_actual": round(self._step_count * self._brain.dt * 1000),
            "initialization_seconds": self.initialization_seconds,
            "average_decision_ms": (
                sum(self._latencies) / len(self._latencies) if self._latencies else None
            ),
            "neural_state_persists_between_decisions": True,
            "neural_state_survives_restart": False,
        }

    def choose_binary(self, context: BrainContext) -> bool:
        return bool(self._run_decision(context, option_count=None).index)

    def choose_option(self, context: BrainContext, options: list[str]) -> int:
        if not options:
            raise ValueError("Brain cannot choose from an empty option list")
        return self._run_decision(context, option_count=len(options)).index

    def get_activity_snapshot(self) -> BrainActivity:
        with self._lock:
            return self._last

    def _population(self, types: tuple[str, ...], side: str) -> np.ndarray:
        key = (types, side)
        if key not in self._population_cache:
            indices = self._brain.cells(list(types), side=side)
            if not len(indices):
                raise RuntimeError(f"MaleCNS population not found: {types} side={side}")
            self._population_cache[key] = indices
        return self._population_cache[key]

    def _injections(self, encoded: EncodedStimulus) -> tuple[list, list[dict]]:
        injections = []
        activity = []
        for drive in encoded.drives:
            indices = self._population(drive.neuron_types, drive.side)
            injections.append((indices, np.float32(drive.amount)))
            activity.append({
                "name": drive.name,
                "population": "+".join(drive.neuron_types),
                "side": drive.side,
                "magnitude": round(drive.amount, 4),
                "neurons": int(len(indices)),
            })
        return injections, activity

    def _run_decision(self, context: BrainContext, option_count: int | None):
        with self._lock:
            encoded = self._encoder.encode(context)
            injections, input_activity = self._injections(encoded)
            spike_counts = np.zeros(self._brain.n, dtype=np.int32)
            active = np.zeros(self._brain.n, dtype=bool)
            step_rates = []
            started = time.perf_counter()
            for _ in range(self._step_count):
                fired = np.asarray(self._brain.step(inject=injections), dtype=np.int64)
                if len(fired):
                    np.add.at(spike_counts, fired, 1)
                    active[fired] = True
                step_rates.append(float(len(fired) / (self._brain.n * self._brain.dt)))
            latency_ms = (time.perf_counter() - started) * 1000
            self._latencies.append(latency_ms)
            duration = self._step_count * self._brain.dt
            action = self._decoder.decode(spike_counts, duration, option_count)
            for (indices, _), readout in zip(injections, input_activity):
                population_spikes = int(spike_counts[indices].sum())
                readout["spikes"] = population_spikes
                readout["spike_rate"] = float(population_spikes / (len(indices) * duration))
            total_spikes = int(spike_counts.sum())
            mean_rate = total_spikes / (self._brain.n * duration)
            self._decision_count += 1
            self._last = BrainActivity(
                activation=min(1.0, mean_rate / 50.0),
                firing_rate=mean_rate,
                dominant_region=action.label,
                spikes=[min(1.0, value / 50.0) for value in step_rates],
                decision_count=self._decision_count,
                backend="connectome",
                dataset=DATASET_NAME,
                neuron_count=self._brain.n,
                connection_count=self._connection_count,
                device=self._brain.device,
                mean_activity=total_spikes / (self._brain.n * self._step_count),
                active_neurons=int(active.sum()),
                spike_rate=mean_rate,
                input_activity=input_activity,
                output_activity=[dict(score) for score in action.scores],
                sampled_neurons=np.flatnonzero(active)[:32].astype(int).tolist(),
                visual_neurons=[{
                    "body_id": body_id,
                    "spike_count": int(spike_counts[index]),
                    "spike_rate": float(spike_counts[index] / duration),
                } for body_id, index in self._visual_indices.items()],
                decision_latency_ms=latency_ms,
            )
            return action
