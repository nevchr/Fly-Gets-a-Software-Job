"""Deterministic simulator-state to sensory-population encoding.

These numbers are interface design, not biological semantics. They drive
documented MaleCNS visual projection neurons while leaving the connectome fixed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from statistics import fmean

from app.simulator.brain.base import BrainContext


CATEGORIES = [
    "Big-O", "arrays", "linked lists", "recursion", "operating systems",
    "networking", "databases", "C", "Python", "Java", "Git",
]
STAGE_ORDER = [
    "SEARCHING_FOR_JOB", "VIEWING_JOB", "DECIDING_TO_APPLY", "APPLICATION_SENT",
    "APPLICATION_RESULT", "RECRUITER_SCREEN", "TECHNICAL_INTERVIEW",
    "BEHAVIORAL_INTERVIEW", "FINAL_RESULT",
]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def normalize(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        raise ValueError("normalization maximum must exceed minimum")
    return clamp((float(value) - minimum) / (maximum - minimum))


def stable_fraction(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 0xFFFFFFFF


@dataclass(frozen=True)
class SensoryDrive:
    name: str
    neuron_types: tuple[str, ...]
    side: str
    amount: float


@dataclass(frozen=True)
class EncodedStimulus:
    features: dict[str, float]
    drives: tuple[SensoryDrive, ...]


class SensoryEncoder:
    """Normalize a BrainContext and map it to documented visual pathways."""

    def encode(self, context: BrainContext) -> EncodedStimulus:
        s = context.signals
        work_mode = str(s.get("work_mode", "hybrid")).lower()
        category = str(s.get("category", "Big-O"))
        absurd_text = str(s.get("absurd_requirement", "")).lower()
        absurd_hits = sum(
            token in absurd_text
            for token in ("years", "family", "passion", "billion", "many hats", "nine daily")
        )
        category_index = CATEGORIES.index(category) if category in CATEGORIES else 0
        stage_text = str(context.stage)
        stage_index = STAGE_ORDER.index(stage_text) if stage_text in STAGE_ORDER else 0

        features = {
            "salary_normalized": normalize(float(s.get("salary", 90_000)), 40_000, 200_000),
            "experience_gap": normalize(float(s.get("required_experience_years", 0)), 0, 10),
            "tech_stack_match": clamp(float(s.get("qualification_match", 0.5))),
            "remote_score": {"remote": 1.0, "hybrid": 0.55, "onsite": 0.1}.get(work_mode, 0.5),
            "job_difficulty": normalize(float(s.get("job_difficulty", s.get("difficulty", 1))), 1, 5),
            "application_length": normalize(float(s.get("application_length", 4)), 1, 40),
            "company_prestige": stable_fraction(str(s.get("company_name", "unknown"))),
            "absurdity_score": clamp(float(s.get("absurdity_score", absurd_hits / 3))),
            "question_difficulty": normalize(float(s.get("question_difficulty", 1)), 1, 3),
            "category_embedding": category_index / max(1, len(CATEGORIES) - 1),
            "number_of_choices": normalize(float(s.get("number_of_choices", 2)), 2, 6),
            "previous_answer_correct": 1.0 if bool(s.get("previous_answer_correct", False)) else 0.0,
            "recent_accuracy": clamp(float(s.get("recent_accuracy", 0.5))),
            "interview_stage": stage_index / max(1, len(STAGE_ORDER) - 1),
            "recent_rejection_streak": normalize(float(s.get("recent_rejection_streak", 0)), 0, 12),
            "company_desirability": clamp(float(s.get("company_desirability", s.get("qualification_match", 0.5)))),
            "current_performance": clamp(float(s.get("current_performance", s.get("recent_accuracy", 0.5)))),
        }
        positive = fmean(features[key] for key in (
            "salary_normalized", "tech_stack_match", "remote_score",
            "company_prestige", "current_performance",
        ))
        negative = fmean(features[key] for key in (
            "experience_gap", "job_difficulty", "application_length",
            "absurdity_score", "recent_rejection_streak",
        ))
        uncertainty = fmean((
            features["question_difficulty"],
            1.0 - features["recent_accuracy"],
            features["number_of_choices"],
        ))
        drives = (
            SensoryDrive("approach", ("LC10a",), "L", clamp(0.10 + 0.50 * positive, 0, 0.65)),
            SensoryDrive("avoidance", ("LC10a",), "R", clamp(0.10 + 0.50 * negative, 0, 0.65)),
            SensoryDrive("threat", ("LC4",), "R", clamp(0.05 + 0.45 * max(features["job_difficulty"], features["absurdity_score"]), 0, 0.65)),
            SensoryDrive("looming_work", ("LPLC2",), "R", clamp(0.05 + 0.40 * max(features["experience_gap"], features["application_length"]), 0, 0.65)),
            SensoryDrive("choice_uncertainty", ("LPLC1",), "L", clamp(0.05 + 0.40 * uncertainty, 0, 0.65)),
        )
        return EncodedStimulus(features=features, drives=drives)

