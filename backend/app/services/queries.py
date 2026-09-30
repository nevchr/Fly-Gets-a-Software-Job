from sqlalchemy import case, func, select

from app.models import CareerStats, InterviewAttempt, JobApplication, SimulationEvent, SimulationState
from app.schemas import (
    CategoryAccuracy,
    EventResponse,
    InterviewStatsResponse,
    JobResponse,
    StatsResponse,
    StatusResponse,
)
from app.simulator.states import STAGE_LABELS, SimulationStage
from app.simulator.clock import clock_minutes, day_phase, is_daytime


class SimulationQueries:
    def __init__(self, session_factory, brain, tick_seconds: float = 4.5):
        self.Session = session_factory
        self.brain = brain
        self.tick_seconds = tick_seconds

    def status(self) -> StatusResponse:
        with self.Session() as session:
            state = session.get(SimulationState, 1)
            stats = session.get(CareerStats, 1)
            stage = SimulationStage(state.stage)
            return StatusResponse(
                stage=stage,
                stage_label=STAGE_LABELS[stage],
                tick_count=state.tick_count,
                simulated_day=max(1, int(stats.simulated_days_unemployed) + 1),
                clock_minutes=clock_minutes(state.tick_count),
                day_phase=day_phase(state.tick_count),
                is_daytime=is_daytime(state.tick_count),
                tick_seconds=self.tick_seconds,
                current_status=stats.current_status,
                current_company=stats.current_company,
                current_job_title=stats.current_job_title,
                brain_activity=self.brain.get_activity_snapshot().to_dict(),
            )

    def stats(self) -> StatsResponse:
        with self.Session() as session:
            return StatsResponse.model_validate(session.get(CareerStats, 1))

    def current_job(self) -> JobResponse | None:
        with self.Session() as session:
            state = session.get(SimulationState, 1)
            if not state.active_application_id:
                return None
            job = session.get(JobApplication, state.active_application_id)
            return JobResponse.model_validate(job) if job else None

    def events(self, limit: int = 100) -> list[EventResponse]:
        with self.Session() as session:
            rows = session.scalars(
                select(SimulationEvent).order_by(SimulationEvent.id.desc()).limit(limit)
            ).all()
            return [
                EventResponse(
                    id=row.id,
                    timestamp=row.timestamp,
                    type=row.type,
                    message=row.message,
                    metadata=row.event_metadata or {},
                )
                for row in rows
            ]

    def interview_stats(self) -> InterviewStatsResponse:
        with self.Session() as session:
            grouped = session.execute(
                select(
                    InterviewAttempt.category,
                    func.count(InterviewAttempt.id),
                    func.sum(case((InterviewAttempt.is_correct.is_(True), 1), else_=0)),
                ).group_by(InterviewAttempt.category)
            ).all()
            categories = []
            total = 0
            correct = 0
            for category, attempts, correct_count in grouped:
                correct_count = int(correct_count or 0)
                total += attempts
                correct += correct_count
                categories.append(CategoryAccuracy(
                    category=category,
                    attempts=attempts,
                    correct=correct_count,
                    accuracy=correct_count / attempts if attempts else 0.0,
                ))
            latest = session.scalar(
                select(InterviewAttempt).order_by(InterviewAttempt.id.desc()).limit(1)
            )
            latest_payload = None
            if latest:
                latest_payload = {
                    "question": latest.prompt,
                    "choices": latest.choices,
                    "selected_index": latest.selected_index,
                    "correct_index": latest.correct_index,
                    "is_correct": latest.is_correct,
                    "category": latest.category,
                    "difficulty": latest.difficulty,
                }
            return InterviewStatsResponse(
                total=total,
                correct=correct,
                accuracy=correct / total if total else 0.0,
                categories=categories,
                latest_attempt=latest_payload,
            )
