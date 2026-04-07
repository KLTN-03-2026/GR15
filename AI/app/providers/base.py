from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class CoverLetterContext:
    candidate_name: str
    job_title: str
    company_name: str
    tone: str
    featured_skills: list[str] = field(default_factory=list)
    job_focus_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    experience_summary: str = ""
    matching_score: float | None = None
    matching_explanation: str | None = None


class CoverLetterProvider(Protocol):
    def generate(self, context: CoverLetterContext) -> str:
        ...
