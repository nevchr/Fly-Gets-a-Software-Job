from datetime import datetime, timezone

from sqlalchemy import func, select

from app.models import CareerStats, InterviewAttempt, JobApplication, SimulationState
from app.simulator.clock import advance_simulated_days, clock_minutes, day_phase, is_daytime
from app.simulator.states import SimulationStage
from conftest import ScriptedBrain


def test_simulated_clock_has_a_long_day_and_preserves_career_day_count():
    assert clock_minutes(0) == 8 * 60
    assert clock_minutes(44) == 19 * 60
    assert not is_daytime(44)
    assert clock_minutes(92) == 7 * 60
    assert is_daytime(92)
    assert day_phase(96) == day_phase(0)
    assert int(advance_simulated_days(4387.125, 63, 64)) == 4388


def test_night_allows_application_but_defers_hiring_decisions(make_simulator, database):
    brain = ScriptedBrain(binaries=[True, True], options=[0])
    engine, _ = make_simulator(brain)
    _, Session, _ = database
    engine.tick()
    with Session.begin() as session:
        state = session.get(SimulationState, 1)
        state.stage = SimulationStage.DECIDING_TO_APPLY
        state.tick_count = 63

    sent = engine.tick()
    assert sent[0]["type"] == "APPLICATION_SENT"
    engine.tick()  # The automated screen may receive the application overnight.
    before_decisions = brain.decisions
    queued = engine.tick()
    assert queued[0]["type"] == "APPLICATION_QUEUED"
    with Session() as session:
        state = session.get(SimulationState, 1)
        stats = session.get(CareerStats, 1)
        assert state.stage == SimulationStage.SEARCHING_FOR_JOB
        assert session.get(JobApplication, 1).status == "awaiting_reply"
        assert stats.applications_sent == 1
        assert brain.decisions == before_decisions

    engine.tick()  # Search for the next job instead of staring at the inbox.
    engine.tick()
    engine.tick()
    with Session() as session:
        assert session.scalar(select(func.count(JobApplication.id))) == 2
        assert session.get(CareerStats, 1).applications_sent == 2
    engine.tick()
    engine.tick()

    with Session.begin() as session:
        session.get(SimulationState, 1).tick_count = 91  # 6:45 AM
    morning = engine.tick()
    assert morning[0]["type"] == "HIRING_RESUMED"
    with Session() as session:
        assert session.get(SimulationState, 1).active_application_id == 1
    outcome = engine.tick()
    assert outcome[0]["type"] == "APPLICATION_REJECTED"


def test_interview_in_progress_pauses_at_night_without_recording_an_answer(make_simulator, database):
    brain = ScriptedBrain(options=[0], binaries=[False])
    engine, _ = make_simulator(brain)
    _, Session, _ = database
    engine.tick()
    with Session.begin() as session:
        state = session.get(SimulationState, 1)
        state.stage = SimulationStage.TECHNICAL_INTERVIEW
        state.tick_count = 43  # 6:45 PM
        job = session.get(JobApplication, state.active_application_id)
        job.applied_at = datetime.now(timezone.utc)

    assert engine.tick() == []
    with Session() as session:
        assert session.get(SimulationState, 1).stage == SimulationStage.TECHNICAL_INTERVIEW
        assert session.query(InterviewAttempt).count() == 0
        assert brain.decisions == 0
        assert session.get(CareerStats, 1).current_status == "Interview paused until 7:00 AM"

    with Session.begin() as session:
        session.get(SimulationState, 1).tick_count = 91
    resumed = engine.tick()
    assert resumed[0]["type"] == "TECHNICAL_ANSWERED"
    with Session() as session:
        assert session.query(InterviewAttempt).count() == 1
