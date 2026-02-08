from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AWGSClassification(str, Enum):
    NORMAL = "normal"
    AT_RISK = "at_risk"
    POSSIBLE_SARCOPENIA = "possible_sarcopenia"


@dataclass(frozen=True)
class AWGSCutoffs:
    sarc_f_threshold: int = 4
    calf_male_cm: float = 34.0
    calf_female_cm: float = 33.0
    handgrip_male_kg: float = 28.0
    handgrip_female_kg: float = 18.0


class AWGS2025Screener:
    """Simplified AWGS 2025 screening logic for MVP scaffolding."""

    def __init__(self, cutoffs: AWGSCutoffs | None = None) -> None:
        self.cutoffs = cutoffs or AWGSCutoffs()

    def screen(
        self,
        *,
        gender: str,
        sarc_f: int | None,
        calf_circumference_cm: float | None,
        handgrip_strength_kg: float | None,
    ) -> dict[str, object]:
        risks: list[str] = []
        screening_positive = False

        if sarc_f is not None and sarc_f >= self.cutoffs.sarc_f_threshold:
            screening_positive = True
            risks.append(f"SARC-F {sarc_f}점")

        if calf_circumference_cm is not None:
            threshold = (
                self.cutoffs.calf_male_cm
                if gender == "male"
                else self.cutoffs.calf_female_cm
            )
            if calf_circumference_cm < threshold:
                screening_positive = True
                risks.append(f"종아리 둘레 {calf_circumference_cm}cm")

        if not screening_positive:
            return {
                "classification": AWGSClassification.NORMAL,
                "screening_positive": False,
                "risk_factors": risks,
            }

        if handgrip_strength_kg is None:
            return {
                "classification": AWGSClassification.AT_RISK,
                "screening_positive": True,
                "risk_factors": risks,
                "recommendations": ["악력 측정 필요"],
            }

        grip_threshold = (
            self.cutoffs.handgrip_male_kg
            if gender == "male"
            else self.cutoffs.handgrip_female_kg
        )
        if handgrip_strength_kg < grip_threshold:
            return {
                "classification": AWGSClassification.POSSIBLE_SARCOPENIA,
                "screening_positive": True,
                "risk_factors": risks,
            }

        return {
            "classification": AWGSClassification.AT_RISK,
            "screening_positive": True,
            "risk_factors": risks,
        }
