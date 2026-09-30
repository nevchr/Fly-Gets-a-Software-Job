import os

import pytest

from app.simulator.brain import BrainAdapter, BrainContext
from app.simulator.brain.fly_connectome import FlyConnectomeAdapter, VISUAL_BODY_IDS


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("RUN_FLYBRAIN_INTEGRATION") != "1",
    reason="set RUN_FLYBRAIN_INTEGRATION=1 to load the 260 MB MaleCNS data",
)
def test_real_connectome_makes_a_binary_decision():
    adapter = FlyConnectomeAdapter(decision_ms=40)
    decision = adapter.choose_binary(BrainContext(
        "apply_to_job",
        "DECIDING_TO_APPLY",
        {"salary": 120_000, "qualification_match": 0.7, "work_mode": "remote"},
    ))
    activity = adapter.get_activity_snapshot()

    assert isinstance(adapter, BrainAdapter)
    assert isinstance(decision, bool)
    assert activity.backend == "connectome"
    assert activity.neuron_count == 166_700
    assert activity.connection_count == 25_582_938
    assert activity.input_activity
    assert all(input_group["spikes"] >= 0 and input_group["spike_rate"] >= 0
               for input_group in activity.input_activity)
    assert activity.output_activity
    assert [sample["body_id"] for sample in activity.visual_neurons] == list(VISUAL_BODY_IDS)
    assert all(sample["spike_count"] >= 0 for sample in activity.visual_neurons)
    assert all(sample["spike_rate"] >= 0 for sample in activity.visual_neurons)
    by_id = {sample["body_id"]: sample for sample in activity.visual_neurons}
    outputs = {output["name"]: output for output in activity.output_activity}
    assert by_id[523769]["spike_count"] == outputs["true / approach"]["spikes"]
    assert by_id[10360]["spike_count"] == outputs["false / avoid"]["spikes"]
