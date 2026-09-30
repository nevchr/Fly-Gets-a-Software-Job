from pathlib import Path

import pytest

from app.config import Settings
from app.simulator.brain import BrainAdapter, MockBrainAdapter, create_brain_adapter
from app.simulator.brain.fly_connectome import FlyConnectomeAdapter


def test_adapters_implement_brain_interface():
    assert issubclass(MockBrainAdapter, BrainAdapter)
    assert issubclass(FlyConnectomeAdapter, BrainAdapter)


def test_mock_backend_can_be_selected_without_connectome_data():
    adapter = create_brain_adapter(Settings(brain_backend="mock"))
    assert isinstance(adapter, MockBrainAdapter)
    assert adapter.backend_name == "mock"


def test_invalid_backend_fails_clearly():
    with pytest.raises(ValueError, match="connectome or mock"):
        create_brain_adapter(Settings(brain_backend="imaginary"))


def test_connectome_mode_fails_clearly_when_data_is_missing(tmp_path: Path):
    with pytest.raises(RuntimeError, match="flybrain download"):
        FlyConnectomeAdapter(data_dir=tmp_path)

