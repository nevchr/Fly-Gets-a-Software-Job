from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventResponse(BaseModel):
    id: int
    timestamp: datetime
    type: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    simulation_start_time: datetime
    simulated_days_unemployed: float
    jobs_viewed: int
    jobs_skipped: int
    applications_sent: int
    immediate_rejections: int
    ghosted: int
    recruiter_screens: int
    technical_interviews: int
    behavioral_interviews: int
    final_rounds: int
    offers: int
    accepted_offers: int
    rejected_offers: int
    total_interview_questions: int
    correct_interview_answers: int
    current_rejection_streak: int
    longest_rejection_streak: int
    highest_salary_applied_to: int
    lowest_qualification_match: float | None
    fastest_rejection_seconds: float | None
    longest_application_streak: int
    current_status: str
    current_company: str | None
    current_job_title: str | None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    title: str
    salary: int
    work_mode: str
    required_experience_years: int
    tech_stack: list[str]
    difficulty: int
    application_length: int
    absurd_requirement: str
    qualification_match: float
    status: str
    created_at: datetime


class VisualNeuronActivityResponse(BaseModel):
    body_id: int
    spike_count: int
    spike_rate: float


class BrainActivityResponse(BaseModel):
    activation: float
    firing_rate: float
    dominant_region: str
    spikes: list[float]
    decision_count: int
    backend: str
    dataset: str | None
    neuron_count: int
    connection_count: int
    device: str
    mean_activity: float
    active_neurons: int
    spike_rate: float
    input_activity: list[dict[str, Any]]
    output_activity: list[dict[str, Any]]
    sampled_neurons: list[int]
    visual_neurons: list[VisualNeuronActivityResponse]
    decision_latency_ms: float


class StatusResponse(BaseModel):
    stage: str
    stage_label: str
    tick_count: int
    simulated_day: int
    clock_minutes: int
    day_phase: float
    is_daytime: bool
    tick_seconds: float
    current_status: str
    current_company: str | None
    current_job_title: str | None
    brain_activity: BrainActivityResponse


class CategoryAccuracy(BaseModel):
    category: str
    attempts: int
    correct: int
    accuracy: float


class InterviewStatsResponse(BaseModel):
    total: int
    correct: int
    accuracy: float
    categories: list[CategoryAccuracy]
    latest_attempt: dict[str, Any] | None


class LiveUpdate(BaseModel):
    kind: str = "simulation_update"
    events: list[EventResponse]
    status: StatusResponse
    stats: StatsResponse
    current_job: JobResponse | None
