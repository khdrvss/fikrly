from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Company


@dataclass
class Assessment:
    score: float
    label: str


def compute_assessment(rating: float, review_count: int) -> Assessment:
    # Wilson score/confidence-inspired scoring
    # Base score from avg rating normalized to 0..1
    base = max(0.0, min(1.0, float(rating) / 5.0))
    # Confidence weight: more reviews -> closer to base
    # k controls smoothing (higher = more smoothing)
    k = 50.0
    weight = review_count / (review_count + k)
    score = (0.5 * (1 - weight)) + (base * weight)

    if score >= 0.85:
        label = "Ajoyib"
    elif score >= 0.7:
        label = "Yaxshi"
    elif score >= 0.55:
        label = "O'rtacha"
    else:
        label = "Past"

    return Assessment(score=round(score * 100, 1), label=label)
