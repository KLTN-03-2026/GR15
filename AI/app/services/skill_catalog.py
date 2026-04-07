from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


SKILL_ALIASES_PATH = Path(__file__).resolve().parents[2] / "data" / "skill_aliases.json"


def _load_skill_catalog() -> list[dict]:
    with SKILL_ALIASES_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("skill_aliases.json phai la mot mang JSON.")

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Moi phan tu trong skill_aliases.json phai la object.")
        if not item.get("skill_name") or not isinstance(item.get("aliases"), list):
            raise ValueError("Moi skill phai co skill_name va aliases hop le.")

    return data


SKILL_CATALOG = _load_skill_catalog()


DEFAULT_SECTION_WEIGHTS = {
    "header": 0.05,
    "skills": 0.35,
    "experience": 0.25,
    "projects": 0.22,
    "education": 0.1,
    "certifications": 0.1,
    "requirements": 0.35,
    "benefits": 0.08,
    "general": 0.15,
}


def normalize_search_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    without_diacritics = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return without_diacritics.lower()


def extract_skills_from_text(
    text: str,
    *,
    section_contexts: dict[str, str] | None = None,
    section_weights: dict[str, float] | None = None,
) -> list[dict]:
    normalized_text = normalize_search_text(text)
    section_contexts = section_contexts or {}
    normalized_contexts = {
        name: normalize_search_text(value)
        for name, value in section_contexts.items()
        if value
    }
    section_weights = section_weights or DEFAULT_SECTION_WEIGHTS

    results = []

    for item in SKILL_CATALOG:
        best_alias = None
        best_score = 0.0

        for alias in item["aliases"]:
            alias_search = normalize_search_text(alias)
            pattern = r"(?<!\w)" + re.escape(alias_search) + r"(?!\w)"

            full_hits = len(re.findall(pattern, normalized_text))
            if not full_hits:
                continue

            score = min(0.45 + full_hits * 0.08, 0.68)
            for section_name, section_text in normalized_contexts.items():
                section_hits = len(re.findall(pattern, section_text))
                if section_hits:
                    score += section_weights.get(section_name, 0.12)

            if score > best_score:
                best_score = score
                best_alias = alias

        if not best_alias:
            continue

        results.append(
            {
                "skill_name": item["skill_name"],
                "category": item["category"],
                "matched_text": best_alias,
                "confidence": round(min(best_score, 0.98), 2),
            }
        )

    results.sort(key=lambda skill: (-skill["confidence"], skill["skill_name"]))
    return results
