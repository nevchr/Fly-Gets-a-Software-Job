from datetime import datetime, timezone

from sqlalchemy import func, select

from app.models import CareerStats, InterviewAttempt, JobApplication, SimulationState
from app.simulator.states import SimulationStage
from conftest import ScriptedBrain


def test_state_machine_advances_through_job_view(make_simulator, database):
    engine, _ = make_simulator()
    _, Session, _ = database

    engine.tick()
    with Session() as session:
        state = session.get(SimulationState, 1)
        stats = session.get(CareerStats, 1)
        assert state.stage == SimulationStage.VIEWING_JOB
        assert state.active_application_id is not None
        assert stats.jobs_viewed == 1

    engine.tick()
    with Session() as session:
        assert session.get(SimulationState, 1).stage == SimulationStage.DECIDING_TO_APPLY


def test_application_decision_updates_career_statistics(make_simulator, database):
    brain = ScriptedBrain(binaries=[True])
    engine, _ = make_simulator(brain)
    _, Session, _ = database
    engine.tick()
    engine.tick()
    engine.tick()

    with Session() as session:
        stats = session.get(CareerStats, 1)
        application = session.get(JobApplication, 1)
        assert stats.applications_sent == 1
        assert stats.highest_salary_applied_to == application.salary
        assert stats.lowest_qualification_match == application.qualification_match
        assert application.status == "applied"


def test_immediate_rejection_outcome_is_recorded(make_simulator, database):
    engine, _ = make_simulator(ScriptedBrain(options=[0]))
    _, Session, _ = database
    engine.tick()
    with Session.begin() as session:
        state = session.get(SimulationState, 1)
        job = session.get(JobApplication, 1)
        state.stage = SimulationStage.APPLICATION_RESULT
        job.applied_at = datetime.now(timezone.utc)
        job.status = "applied"

    events = engine.tick()
    with Session() as session:
        stats = session.get(CareerStats, 1)
        assert stats.immediate_rejections == 1
        assert stats.current_rejection_streak == 1
        assert session.get(JobApplication, 1).status == "rejected"
        assert session.get(SimulationState, 1).stage == SimulationStage.SEARCHING_FOR_JOB
    assert events[0]["type"] == "APPLICATION_REJECTED"


def test_interview_attempt_and_accuracy_are_persisted(make_simulator, database):
    engine, _ = make_simulator(ScriptedBrain(options=[0], binaries=[False]))
    _, Session, _ = database
    engine.tick()
    with Session.begin() as session:
        session.get(SimulationState, 1).stage = SimulationStage.TECHNICAL_INTERVIEW

    engine.tick()
    with Session() as session:
        attempt = session.scalar(select(InterviewAttempt))
        stats = session.get(CareerStats, 1)
        assert attempt is not None
        assert attempt.is_correct is True
        assert stats.total_interview_questions == 1
        assert stats.correct_interview_answers == 1
        assert session.scalar(select(func.count(InterviewAttempt.id))) == 1

