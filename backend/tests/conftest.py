from collections import deque
import os

import pytest

os.environ["BRAIN_BACKEND"] = "mock"

from app.database import initialize_database, make_engine, make_session_factory
from app.simulator.brain import BrainActivity, BrainAdapter, BrainContext
from app.simulator.engine import SimulationEngine


class ScriptedBrain(BrainAdapter):
    def __init__(self, binaries=(), options=()):
        self.binaries = deque(binaries)
        self.options = deque(options)
        self.decisions = 0

    def choose_binary(self, context: BrainContext) -> bool:
        self.decisions += 1
        return self.binaries.popleft() if self.binaries else False

    def choose_option(self, context: BrainContext, options: list[str]) -> int:
        self.decisions += 1
        return self.options.popleft() if self.options else 0

    def get_activity_snapshot(self) -> BrainActivity:
        return BrainActivity(0.5, 50.0, "test circuit", [0.0, 1.0], self.decisions)


@pytest.fixture
def database(tmp_path):
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    engine = make_engine(url)
    initialize_database(engine)
    yield engine, make_session_factory(engine), url
    engine.dispose()


@pytest.fixture
def make_simulator(database):
    _, Session, _ = database

    def factory(brain=None):
        chosen_brain = brain or ScriptedBrain()
        return SimulationEngine(Session, chosen_brain, seed=101, max_events=50), chosen_brain

    return factory
