from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class CoverLetterContext:
    candidate_name: str
    job_title: str
    company_name: str
    tone: str
    candidate_title: str | None = None
    career_goal: str | None = None
    education_level: str | None = None
    years_experience: float | int | None = None
    job_level: str | None = None
    required_experience: str | None = None
    required_education: str | None = None
    featured_skills: list[str] = field(default_factory=list)
    job_focus_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    candidate_evidence: list[str] = field(default_factory=list)
    job_evidence: list[str] = field(default_factory=list)
    experience_summary: str = ""
    matching_score: float | None = None
    matching_explanation: str | None = None
    score_breakdown: dict = field(default_factory=dict)


class CoverLetterProvider(Protocol):
    def generate(self, context: CoverLetterContext) -> str:
        ...
