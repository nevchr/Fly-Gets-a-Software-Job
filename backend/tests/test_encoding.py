from app.simulator.brain import BrainContext
from app.simulator.brain.encoding import SensoryEncoder, normalize


def test_normalization_is_clamped_and_deterministic():
    assert normalize(40_000, 40_000, 200_000) == 0.0
    assert normalize(120_000, 40_000, 200_000) == 0.5
    assert normalize(300_000, 40_000, 200_000) == 1.0


def test_job_context_encodes_expected_features_and_real_populations():
    context = BrainContext(
        "apply_to_job",
        "DECIDING_TO_APPLY",
        {
            "salary": 120_000,
            "required_experience_years": 5,
            "qualification_match": 0.75,
            "work_mode": "remote",
            "job_difficulty": 3,
            "application_length": 20,
            "company_name": "Macrohard",
            "absurd_requirement": "Entry-level position requiring 5+ years",
        },
    )
    encoder = SensoryEncoder()
    first = encoder.encode(context)
    second = encoder.encode(context)

    assert first == second
    assert first.features["salary_normalized"] == 0.5
    assert first.features["experience_gap"] == 0.5
    assert first.features["remote_score"] == 1.0
    assert {drive.neuron_types for drive in first.drives} == {
        ("LC10a",), ("LC4",), ("LPLC2",), ("LPLC1",),
    }
    assert all(0.0 <= drive.amount <= 0.65 for drive in first.drives)


def test_technical_encoding_does_not_depend_on_correct_answer():
    encoder = SensoryEncoder()
    base = {
        "category": "Python",
        "question_difficulty": 2,
        "number_of_choices": 4,
        "recent_accuracy": 0.6,
    }
    a = encoder.encode(BrainContext("technical_answer", "TECHNICAL_INTERVIEW", base))
    b = encoder.encode(BrainContext(
        "technical_answer", "TECHNICAL_INTERVIEW", {**base, "correct_index": 3}
    ))
    assert a == b

