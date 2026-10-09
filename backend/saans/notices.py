"""Deterministic parent notices (EN/HI). No LLM: every number comes from the DayPlan."""
from __future__ import annotations

from urllib.parse import quote

from .models import DayPlan

BAND_HI = {
    "Good": "अच्छी", "Satisfactory": "संतोषजनक", "Moderate": "मध्यम",
    "Poor": "खराब", "Very Poor": "बहुत खराब", "Severe": "गंभीर",
}
MODE_NOTE = {
    "en": {"fixture": "(Sample data)", "replay": "(Replay of recorded data)", "cached": "(Cached data)"},
    "hi": {"fixture": "(नमूना डेटा)", "replay": "(रिकॉर्ड किया गया डेटा)", "cached": "(कैश्ड डेटा)"},
}


def whatsapp_url(text: str) -> str:
    return "https://wa.me/?text=" + quote(text, safe="")


def build_notice(plan: DayPlan, lang: str = "en") -> dict:
    hi = lang == "hi"
    outdoor = [p for p in plan.periods if p.period.outdoor]
    lines: list[str] = []
    if not outdoor:
        lines.append("प्रिय अभिभावकगण,\nआज कोई बाहरी गतिविधि निर्धारित नहीं है।" if hi
                     else "Dear Parents,\nNo outdoor activities are scheduled today.")
    else:
        worst = max(outdoor, key=lambda p: p.aqi)
        band = BAND_HI.get(worst.band, worst.band) if hi else worst.band
        lines.append(
            f"प्रिय अभिभावकगण,\nआज बाहरी गतिविधियों के समय वायु गुणवत्ता {band} (AQI {worst.aqi}) रहने का अनुमान है। बच्चों की सुरक्षा के लिए:"
            if hi else
            f"Dear Parents,\nAir quality during outdoor activities today is forecast as {worst.band} (AQI {worst.aqi}). For student safety:"
        )
        for p in outdoor:
            label = f"{p.period.label} ({p.period.start})"
            text = p.action.text_hi if hi else p.action.text_en
            if p.swap and not p.swap.optional:
                # A swap is a suggestion the school may accept; the notice offers it, it never announces it as done.
                s = p.swap
                sb = BAND_HI.get(s.to_band, s.to_band) if hi else s.to_band
                lines.append(f"• {label}: {text.rstrip('।')}, या {s.to_start} पर करें ({sb}, AQI {s.to_aqi})।" if hi
                             else f"• {label}: {text.rstrip('.')}, or move it to {s.to_start} ({s.to_band}, AQI {s.to_aqi}).")
            else:
                lines.append(f"• {label}: {text}")
        if plan.sources and any(p.sensitive_action.level != "go" for p in outdoor):
            a = max(outdoor, key=lambda p: p.aqi).sensitive_action
            lines.append(f"• अस्थमा वाले विद्यार्थी: {a.text_hi}" if hi else f"• Students with asthma: {a.text_en}")
        lines.append("आपके सहयोग के लिए धन्यवाद।" if hi else "Thank you for your cooperation.")
    note = MODE_NOTE["hi" if hi else "en"].get(plan.mode)
    if note:
        lines.append(note)
    text = "\n".join(lines)
    return {"text": text, "whatsapp_url": whatsapp_url(text), "mode": plan.mode}
