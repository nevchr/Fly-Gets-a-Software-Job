from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select

from app.models import CareerStats, InterviewAttempt, JobApplication, SimulationEvent, SimulationState
from app.simulator.brain import BrainAdapter, BrainContext
from app.simulator.clock import advance_simulated_days, is_daytime
from app.simulator.copy import event_line, stage_status
from app.simulator.interviews import (
    BEHAVIORAL_PROMPTS,
    BEHAVIORAL_SCORES,
    QUESTION_BANK,
    RESPONSE_STYLES,
)
from app.simulator.jobs import JobFactory
from app.simulator.states import SimulationStage


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SimulationEngine:
    """One transactional state-machine step at a time."""

    def __init__(self, session_factory, brain: BrainAdapter, seed: int, max_events: int = 1000):
        self.Session = session_factory
        self.brain = brain
        self.jobs = JobFactory(seed)
        self.max_events = max_events

    def tick(self) -> list[dict[str, Any]]:
        with self.Session.begin() as session:
            state = session.get(SimulationState, 1)
            stats = session.get(CareerStats, 1)
            if state is None or stats is None:
                raise RuntimeError("Database was not initialized")

            previous_tick = state.tick_count
            state.tick_count += 1
            state.updated_at = utcnow()
            stats.simulated_days_unemployed = advance_simulated_days(
                stats.simulated_days_unemployed, previous_tick, state.tick_count
            )
            events: list[SimulationEvent] = []
            stage = SimulationStage(state.stage)
            application = (
                session.get(JobApplication, state.active_application_id)
                if state.active_application_id
                else None
            )

            if not is_daytime(state.tick_count) and stage in {
                SimulationStage.RECRUITER_SCREEN,
                SimulationStage.TECHNICAL_INTERVIEW,
                SimulationStage.BEHAVIORAL_INTERVIEW,
                SimulationStage.FINAL_RESULT,
            }:
                stats.current_status = (
                    "Final hiring decision waits until 7:00 AM"
                    if stage == SimulationStage.FINAL_RESULT
                    else "Interview paused until 7:00 AM"
                )
                return []

            if stage == SimulationStage.SEARCHING_FOR_JOB:
                queued = session.scalar(
                    select(JobApplication)
                    .where(JobApplication.status == "awaiting_reply")
                    .order_by(JobApplication.id)
                    .limit(1)
                ) if is_daytime(state.tick_count) else None
                if queued is not None:
                    application = queued
                    application.status = "applied"
                    state.active_application_id = application.id
                    stats.current_company = application.company_name
                    stats.current_job_title = application.title
                    self._advance(state, stats, SimulationStage.APPLICATION_RESULT)
                    events.append(self._event(
                        "HIRING_RESUMED",
                        event_line("HIRING_RESUMED", application.id, company=application.company_name),
                        application_id=application.id,
                    ))
                else:
                    generated = self.jobs.generate(stats.jobs_viewed + 1)
                    application = JobApplication(**generated.__dict__)
                    session.add(application)
                    session.flush()
                    state.active_application_id = application.id
                    stats.jobs_viewed += 1
                    stats.current_company = application.company_name
                    stats.current_job_title = application.title
                    self._advance(state, stats, SimulationStage.VIEWING_JOB)
                    events.append(self._event(
                        "JOB_FOUND",
                        event_line("JOB_FOUND", application.id, title=application.title, company=application.company_name),
                        application_id=application.id,
                    ))

            elif stage == SimulationStage.VIEWING_JOB:
                self._advance(state, stats, SimulationStage.DECIDING_TO_APPLY)
                year_label = "year" if application.required_experience_years == 1 else "years"
                events.append(self._event(
                    "JOB_VIEWED",
                    event_line(
                        "JOB_VIEWED", application.id,
                        years=application.required_experience_years,
                        year_word=year_label,
                        match_pct=round(application.qualification_match * 100),
                        requirement=application.absurd_requirement,
                    ),
                    match=application.qualification_match,
                ))

            elif stage == SimulationStage.DECIDING_TO_APPLY:
                should_apply = self.brain.choose_binary(BrainContext(
                    decision="apply_to_job",
                    stage=stage,
                    signals=self._job_signals(application, stats),
                ))
                if should_apply:
                    application.status = "applied"
                    application.applied_at = utcnow()
                    stats.applications_sent += 1
                    stats.current_application_streak += 1
                    stats.longest_application_streak = max(
                        stats.longest_application_streak, stats.current_application_streak
                    )
                    stats.highest_salary_applied_to = max(stats.highest_salary_applied_to, application.salary)
                    stats.lowest_qualification_match = (
                        application.qualification_match
                        if stats.lowest_qualification_match is None
                        else min(stats.lowest_qualification_match, application.qualification_match)
                    )
                    self._advance(state, stats, SimulationStage.APPLICATION_SENT)
                    events.append(self._event(
                        "APPLICATION_SENT",
                        event_line("APPLICATION_SENT", application.id, company=application.company_name),
                        application_id=application.id,
                    ))
                else:
                    stats.jobs_skipped += 1
                    stats.current_application_streak = 0
                    application.status = "skipped"
                    events.append(self._event(
                        "JOB_SKIPPED",
                        event_line("JOB_SKIPPED", application.id, company=application.company_name),
                        application_id=application.id,
                    ))
                    self._finish_application(state, stats, application)

            elif stage == SimulationStage.APPLICATION_SENT:
                self._advance(state, stats, SimulationStage.APPLICATION_RESULT)
                events.append(self._event(
                    "RESUME_SCANNED",
                    event_line("RESUME_SCANNED", application.id, company=application.company_name),
                ))

            elif stage == SimulationStage.APPLICATION_RESULT:
                if not is_daytime(state.tick_count):
                    application.status = "awaiting_reply"
                    state.active_application_id = None
                    stats.current_company = None
                    stats.current_job_title = None
                    self._advance(state, stats, SimulationStage.SEARCHING_FOR_JOB)
                    events.append(self._event(
                        "APPLICATION_QUEUED",
                        event_line("APPLICATION_QUEUED", application.id, company=application.company_name),
                        application_id=application.id,
                    ))
                else:
                    outcome_index = self.brain.choose_option(
                        BrainContext("application_outcome", stage, self._job_signals(application, stats)),
                        ["immediate rejection", "ghosted", "recruiter screen"],
                    )
                    if outcome_index == 0:
                        stats.immediate_rejections += 1
                        events.append(self._rejection_event(stats, application, "APPLICATION_REJECTED", "before the interview stage"))
                        self._finish_application(state, stats, application, "rejected")
                    elif outcome_index == 1:
                        stats.ghosted += 1
                        self._record_rejection(stats)
                        events.append(self._event(
                            "APPLICATION_GHOSTED",
                            event_line("APPLICATION_GHOSTED", application.id, company=application.company_name),
                        ))
                        self._finish_application(state, stats, application, "ghosted")
                    else:
                        application.status = "interview"
                        stats.recruiter_screens += 1
                        self._advance(state, stats, SimulationStage.RECRUITER_SCREEN)
                        events.append(self._event(
                            "RECRUITER_SCREEN_BOOKED",
                            event_line("RECRUITER_SCREEN_BOOKED", application.id, company=application.company_name),
                        ))

            elif stage == SimulationStage.RECRUITER_SCREEN:
                passed = self.brain.choose_binary(
                    BrainContext("pass_recruiter_screen", stage, self._job_signals(application, stats))
                )
                if passed:
                    stats.technical_interviews += 1
                    self._advance(state, stats, SimulationStage.TECHNICAL_INTERVIEW)
                    events.append(self._event(
                        "RECRUITER_SCREEN_PASSED",
                        event_line("RECRUITER_SCREEN_PASSED", application.id, company=application.company_name),
                    ))
                else:
                    events.append(self._rejection_event(stats, application, "RECRUITER_REJECTION", "after the recruiter screen"))
                    self._finish_application(state, stats, application, "rejected")

            elif stage == SimulationStage.TECHNICAL_INTERVIEW:
                question = QUESTION_BANK[(state.tick_count + application.id) % len(QUESTION_BANK)]
                recent_accuracy = (
                    stats.correct_interview_answers / stats.total_interview_questions
                    if stats.total_interview_questions else 0.5
                )
                selected = self.brain.choose_option(
                    BrainContext(
                        "technical_answer",
                        stage,
                        {
                            **self._job_signals(application, stats),
                            "category": question.category,
                            "question_difficulty": question.difficulty,
                            "number_of_choices": len(question.choices),
                            "recent_accuracy": recent_accuracy,
                        },
                    ),
                    question.choices,
                )
                correct = selected == question.correct_index
                session.add(InterviewAttempt(
                    application_id=application.id,
                    question_id=question.id,
                    category=question.category,
                    difficulty=question.difficulty,
                    prompt=question.prompt,
                    choices=question.choices,
                    selected_index=selected,
                    correct_index=question.correct_index,
                    is_correct=correct,
                ))
                stats.total_interview_questions += 1
                stats.correct_interview_answers += int(correct)
                events.append(self._event(
                    "TECHNICAL_ANSWERED",
                    event_line(
                        "TECHNICAL_CORRECT" if correct else "TECHNICAL_WRONG",
                        application.id,
                        category=question.category,
                        answer=question.choices[selected],
                    ),
                    question_id=question.id,
                    selected_index=selected,
                    correct=correct,
                ))
                passed = self.brain.choose_binary(BrainContext(
                    "pass_technical",
                    stage,
                    {
                        **self._job_signals(application, stats),
                        "previous_answer_correct": correct,
                        "recent_accuracy": (
                            stats.correct_interview_answers / stats.total_interview_questions
                        ),
                    },
                ))
                if passed:
                    stats.behavioral_interviews += 1
                    self._advance(state, stats, SimulationStage.BEHAVIORAL_INTERVIEW)
                else:
                    events.append(self._rejection_event(stats, application, "TECHNICAL_REJECTION", "after the technical round"))
                    self._finish_application(state, stats, application, "rejected")

            elif stage == SimulationStage.BEHAVIORAL_INTERVIEW:
                prompt = BEHAVIORAL_PROMPTS[(state.tick_count + application.id) % len(BEHAVIORAL_PROMPTS)]
                recent_accuracy = (
                    stats.correct_interview_answers / stats.total_interview_questions
                    if stats.total_interview_questions else 0.5
                )
                style_index = self.brain.choose_option(
                    BrainContext(
                        "behavioral_style",
                        stage,
                        {
                            **self._job_signals(application, stats),
                            "prompt": prompt,
                            "number_of_choices": len(RESPONSE_STYLES),
                            "recent_accuracy": recent_accuracy,
                            "current_performance": recent_accuracy,
                        },
                    ),
                    RESPONSE_STYLES,
                )
                style = RESPONSE_STYLES[style_index]
                events.append(self._event(
                    "BEHAVIORAL_ANSWERED",
                    event_line("BEHAVIORAL_ANSWERED", application.id, prompt=prompt, style=style),
                    response_style=style,
                ))
                passed = self.brain.choose_binary(BrainContext(
                    "pass_behavioral",
                    stage,
                    {
                        **self._job_signals(application, stats),
                        "style": style,
                        "current_performance": BEHAVIORAL_SCORES[style],
                    },
                ))
                if passed:
                    stats.final_rounds += 1
                    self._advance(state, stats, SimulationStage.FINAL_RESULT)
                else:
                    events.append(self._rejection_event(stats, application, "CULTURE_REJECTION", "after the behavioral round"))
                    self._finish_application(state, stats, application, "rejected")

            elif stage == SimulationStage.FINAL_RESULT:
                offered = self.brain.choose_binary(
                    BrainContext("receive_offer", stage, self._job_signals(application, stats))
                )
                if offered:
                    stats.offers += 1
                    self._reset_rejections(stats)
                    accepted = self.brain.choose_binary(
                        BrainContext("accept_offer", stage, self._job_signals(application, stats))
                    )
                    if accepted:
                        stats.accepted_offers += 1
                        event_type = "OFFER_ACCEPTED"
                        message = event_line("OFFER_ACCEPTED", application.id, company=application.company_name)
                        result = "accepted"
                    else:
                        stats.rejected_offers += 1
                        event_type = "OFFER_REJECTED"
                        message = event_line("OFFER_REJECTED", application.id, company=application.company_name)
                        result = "offer_rejected"
                    events.append(self._event(event_type, message, salary=application.salary))
                    self._finish_application(state, stats, application, result)
                else:
                    events.append(self._rejection_event(stats, application, "FINAL_REJECTION", "after final review"))
                    self._finish_application(state, stats, application, "rejected")

            for event in events:
                session.add(event)
            session.flush()
            payloads = [self._event_payload(event) for event in events]
            self._prune_events(session)
            return payloads

    def _advance(self, state: SimulationState, stats: CareerStats, stage: SimulationStage) -> None:
        state.stage = stage
        stats.current_status = stage_status(stage, stats.jobs_viewed)

    @staticmethod
    def _job_signals(application: JobApplication, stats: CareerStats) -> dict[str, Any]:
        return {
            "salary": application.salary,
            "required_experience_years": application.required_experience_years,
            "qualification_match": application.qualification_match,
            "work_mode": application.work_mode,
            "job_difficulty": application.difficulty,
            "application_length": application.application_length,
            "company_name": application.company_name,
            "absurd_requirement": application.absurd_requirement,
            "recent_rejection_streak": stats.current_rejection_streak,
            "company_desirability": application.qualification_match,
        }

    def _finish_application(
        self,
        state: SimulationState,
        stats: CareerStats,
        application: JobApplication,
        result: str | None = None,
    ) -> None:
        application.status = result or application.status
        application.completed_at = utcnow()
        state.active_application_id = None
        stats.current_company = None
        stats.current_job_title = None
        self._advance(state, stats, SimulationStage.SEARCHING_FOR_JOB)

    def _record_rejection(self, stats: CareerStats) -> None:
        stats.current_rejection_streak += 1
        stats.longest_rejection_streak = max(
            stats.longest_rejection_streak, stats.current_rejection_streak
        )

    def _reset_rejections(self, stats: CareerStats) -> None:
        stats.current_rejection_streak = 0

    def _rejection_event(
        self, stats: CareerStats, application: JobApplication, event_type: str, reason: str
    ) -> SimulationEvent:
        self._record_rejection(stats)
        elapsed = 0.1
        if application.applied_at:
            applied_at = application.applied_at
            if applied_at.tzinfo is None:
                applied_at = applied_at.replace(tzinfo=timezone.utc)
            elapsed = max(0.1, (utcnow() - applied_at).total_seconds())
        stats.fastest_rejection_seconds = (
            elapsed
            if stats.fastest_rejection_seconds is None
            else min(stats.fastest_rejection_seconds, elapsed)
        )
        return self._event(
            event_type,
            event_line("REJECTION", application.id, company=application.company_name, reason=reason),
            rejection_seconds=round(elapsed, 2),
        )

    @staticmethod
    def _event(event_type: str, message: str, **metadata) -> SimulationEvent:
        return SimulationEvent(type=event_type, message=message, event_metadata=metadata)

    @staticmethod
    def _event_payload(event: SimulationEvent) -> dict[str, Any]:
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "type": event.type,
            "message": event.message,
            "metadata": event.event_metadata or {},
        }

    def _prune_events(self, session) -> None:
        stale_ids = session.scalars(
            select(SimulationEvent.id)
            .order_by(SimulationEvent.id.desc())
            .offset(self.max_events)
        ).all()
        if stale_ids:
            session.execute(delete(SimulationEvent).where(SimulationEvent.id.in_(stale_ids)))
