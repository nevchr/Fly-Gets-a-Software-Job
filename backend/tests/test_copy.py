from app.simulator.copy import EVENT_LINES, STAGE_STATUS, event_line, stage_status
from app.simulator.interviews import BEHAVIORAL_PROMPTS, QUESTION_BANK
from app.simulator.jobs import JobFactory
from app.simulator.states import SimulationStage


def test_every_stage_has_distinct_status_options():
    assert set(STAGE_STATUS) == set(SimulationStage)
    for stage, choices in STAGE_STATUS.items():
        assert len(choices) >= 8
        assert len(set(choices)) == len(choices)
        assert [stage_status(stage, index) for index in range(1, len(choices) + 1)] == list(choices)


def test_every_event_variant_renders_without_placeholders():
    details = {
        "title": "Junior Engineer",
        "company": "BugByte Labs",
        "years": 3,
        "year_word": "years",
        "match_pct": 42,
        "requirement": "bring a keyboard",
        "category": "Python",
        "answer": "tuple",
        "prompt": "Why this role?",
        "style": "confident",
        "reason": "after the interview",
    }
    for kind, choices in EVENT_LINES.items():
        assert len(choices) >= 8, kind
        rendered = [event_line(kind, index, **details) for index in range(1, len(choices) + 1)]
        assert len(set(rendered)) == len(rendered), kind
        assert all("{" not in line and "}" not in line for line in rendered)


def test_new_job_and_interview_text_have_broad_variety():
    jobs = [JobFactory(314159).generate(index) for index in range(1, 500)]
    assert len({job.company_name for job in jobs}) >= 25
    assert len({job.title for job in jobs}) >= 20
    assert len({job.absurd_requirement for job in jobs}) >= 30
    assert len(BEHAVIORAL_PROMPTS) >= 20
    assert len({question.id for question in QUESTION_BANK}) == len(QUESTION_BANK)
    assert len({question.prompt for question in QUESTION_BANK}) == len(QUESTION_BANK)
    assert all(0 <= question.correct_index < len(question.choices) for question in QUESTION_BANK)
