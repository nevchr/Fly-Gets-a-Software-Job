from app.simulator.brain import BrainContext, MockBrainAdapter


def test_mock_brain_is_deterministic_for_same_seed():
    first = MockBrainAdapter(42)
    second = MockBrainAdapter(42)
    context = BrainContext("test", "TEST", {"threshold": 0.4})

    first_results = [first.choose_binary(context), first.choose_option(context, ["a", "b", "c"])]
    second_results = [second.choose_binary(context), second.choose_option(context, ["a", "b", "c"])]

    assert first_results == second_results
    assert first.get_activity_snapshot().decision_count == 2


def test_brain_rejects_empty_options():
    brain = MockBrainAdapter(1)
    try:
        brain.choose_option(BrainContext("empty", "TEST"), [])
    except ValueError as error:
        assert "empty" in str(error)
    else:
        raise AssertionError("Expected an empty choice list to fail")

