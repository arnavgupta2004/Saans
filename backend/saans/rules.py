"""Deterministic school air-safety actions.

These rules are Saans' conservative school protocol. They deliberately do not
depend on an LLM: callers receive a stable, explainable action and rule ID.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ActionLevel = Literal["go", "caution", "indoors"]


@dataclass(frozen=True)
class Action:
    level: ActionLevel
    text_en: str
    text_hi: str
    rule_id: str


_BANDS = ("Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe")
_INTENSITIES = ("high", "low")


def _activity_name(activity_type: str) -> str:
    return {
        "pe": "PE",
        "sports": "sports",
        "assembly": "assembly",
        "recess": "recess",
        "class": "outdoor class",
    }.get(activity_type, "outdoor activity")


def _normal_action(band: str, intensity: str, activity: str) -> Action:
    """Return the non-sensitive-student cell of the protocol table."""
    rule_id = f"SAANS-{band.upper().replace(' ', '-')}-{intensity.upper()}"
    if band in {"Good", "Satisfactory"}:
        return Action("go", f"Go ahead with {activity} as planned.", "निर्धारित गतिविधि सामान्य रूप से करें।", rule_id)
    if band == "Moderate":
        if intensity == "high":
            return Action(
                "caution",
                f"Go ahead with {activity}, but keep the warm-up short and provide water breaks.",
                "गतिविधि कर सकते हैं, लेकिन वार्म-अप छोटा रखें और पानी के ब्रेक दें।",
                rule_id,
            )
        return Action("go", f"Go ahead with {activity} as planned.", "निर्धारित गतिविधि सामान्य रूप से करें।", rule_id)
    if band == "Poor":
        if intensity == "high":
            return Action(
                "indoors",
                f"Move {activity} indoors or swap it to a cleaner time slot.",
                "गतिविधि को अंदर करें या कम प्रदूषण वाले समय पर बदलें।",
                rule_id,
            )
        return Action(
            "caution",
            f"Keep {activity} outdoors for no more than 15 minutes.",
            "बाहरी गतिविधि को 15 मिनट से अधिक न रखें।",
            rule_id,
        )
    if band == "Very Poor":
        if activity == "assembly":
            return Action(
                "indoors",
                "Hold assembly indoors; use the PA system or classrooms.",
                "असेंबली अंदर करें; पीए सिस्टम या कक्षा का उपयोग करें।",
                rule_id,
            )
        return Action("indoors", f"Hold {activity} indoors.", "गतिविधि अंदर करें।", rule_id)
    return Action(
        "indoors",
        f"Hold {activity} indoors. Inform management and follow state or GRAP directives.",
        "गतिविधि अंदर करें। प्रबंधन को बताएं और राज्य या ग्रैप के निर्देशों का पालन करें।",
        rule_id,
    )


def _sensitive_action(band: str) -> Action:
    """Return the sensitive-student column of the protocol table."""
    rule_id = f"SAANS-{band.upper().replace(' ', '-')}-SENSITIVE"
    if band in {"Good", "Satisfactory"}:
        return Action("go", "Normal routine; ensure an inhaler is available.", "सामान्य दिनचर्या रखें; इनहेलर उपलब्ध रखें।", rule_id)
    if band == "Moderate":
        return Action(
            "caution",
            "Avoid strenuous activity; allow the student to stay indoors.",
            "कठिन गतिविधि से बचें; बच्चे को अंदर रहने का विकल्प दें।",
            rule_id,
        )
    if band == "Poor":
        return Action("indoors", "Keep sensitive students indoors.", "संवेदनशील बच्चों को अंदर रखें।", rule_id)
    if band == "Very Poor":
        return Action(
            "indoors",
            "Keep sensitive students indoors and inform parents.",
            "संवेदनशील बच्चों को अंदर रखें और माता-पिता को बताएं।",
            rule_id,
        )
    return Action(
        "indoors",
        "Keep sensitive students indoors; inform management and follow state or GRAP directives.",
        "संवेदनशील बच्चों को अंदर रखें; प्रबंधन को बताएं और राज्य या ग्रैप के निर्देश मानें।",
        rule_id,
    )


def action_for(activity_type: str, intensity: str, band: str, sensitive: bool = False) -> Action:
    """Return the deterministic safety action for one scheduled activity.

    ``sensitive=True`` selects the table's asthma/sensitive-student column;
    activity intensity is intentionally ignored for that protective column.
    """
    if band not in _BANDS:
        raise ValueError(f"Unsupported AQI band: {band}")
    if intensity not in _INTENSITIES:
        raise ValueError(f"Unsupported activity intensity: {intensity}")
    if sensitive:
        return _sensitive_action(band)
    return _normal_action(band, intensity, _activity_name(activity_type))


INDOOR_ACTION = Action("go", "Indoor class — no change needed", "इनडोर कक्षा — किसी बदलाव की आवश्यकता नहीं", "SAANS-INDOOR")
