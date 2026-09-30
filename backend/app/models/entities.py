from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SimulationState(Base):
    __tablename__ = "simulation_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    stage: Mapped[str] = mapped_column(String(40), default="SEARCHING_FOR_JOB")
    active_application_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_applications.id"), nullable=True
    )
    tick_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CareerStats(Base):
    __tablename__ = "career_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    simulation_start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    simulated_days_unemployed: Mapped[float] = mapped_column(Float, default=0.0)
    jobs_viewed: Mapped[int] = mapped_column(Integer, default=0)
    jobs_skipped: Mapped[int] = mapped_column(Integer, default=0)
    applications_sent: Mapped[int] = mapped_column(Integer, default=0)
    immediate_rejections: Mapped[int] = mapped_column(Integer, default=0)
    ghosted: Mapped[int] = mapped_column(Integer, default=0)
    recruiter_screens: Mapped[int] = mapped_column(Integer, default=0)
    technical_interviews: Mapped[int] = mapped_column(Integer, default=0)
    behavioral_interviews: Mapped[int] = mapped_column(Integer, default=0)
    final_rounds: Mapped[int] = mapped_column(Integer, default=0)
    offers: Mapped[int] = mapped_column(Integer, default=0)
    accepted_offers: Mapped[int] = mapped_column(Integer, default=0)
    rejected_offers: Mapped[int] = mapped_column(Integer, default=0)
    total_interview_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_interview_answers: Mapped[int] = mapped_column(Integer, default=0)
    current_rejection_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_rejection_streak: Mapped[int] = mapped_column(Integer, default=0)
    highest_salary_applied_to: Mapped[int] = mapped_column(Integer, default=0)
    lowest_qualification_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    fastest_rejection_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    longest_application_streak: Mapped[int] = mapped_column(Integer, default=0)
    current_application_streak: Mapped[int] = mapped_column(Integer, default=0)
    current_status: Mapped[str] = mapped_column(String(120), default="scanning the void")
    current_company: Mapped[str | None] = mapped_column(String(120), nullable=True)
    current_job_title: Mapped[str | None] = mapped_column(String(160), nullable=True)


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(160))
    salary: Mapped[int] = mapped_column(Integer)
    work_mode: Mapped[str] = mapped_column(String(20))
    required_experience_years: Mapped[int] = mapped_column(Integer)
    tech_stack: Mapped[list[str]] = mapped_column(JSON)
    difficulty: Mapped[int] = mapped_column(Integer)
    application_length: Mapped[int] = mapped_column(Integer)
    absurd_requirement: Mapped[str] = mapped_column(Text)
    qualification_match: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(40), default="viewing")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    attempts: Mapped[list["InterviewAttempt"]] = relationship(back_populates="application")


class SimulationEvent(Base):
    __tablename__ = "simulation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    type: Mapped[str] = mapped_column(String(60), index=True)
    message: Mapped[str] = mapped_column(Text)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class InterviewAttempt(Base):
    __tablename__ = "interview_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("job_applications.id"))
    question_id: Mapped[str] = mapped_column(String(60))
    category: Mapped[str] = mapped_column(String(40), index=True)
    difficulty: Mapped[int] = mapped_column(Integer)
    prompt: Mapped[str] = mapped_column(Text)
    choices: Mapped[list[str]] = mapped_column(JSON)
    selected_index: Mapped[int] = mapped_column(Integer)
    correct_index: Mapped[int] = mapped_column(Integer)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    application: Mapped[JobApplication] = relationship(back_populates="attempts")

