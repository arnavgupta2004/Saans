import pytest

from saans.rules import action_for


@pytest.mark.parametrize(
    ("band", "intensity", "level"),
    [
        ("Good", "high", "go"),
        ("Good", "low", "go"),
        ("Satisfactory", "high", "go"),
        ("Satisfactory", "low", "go"),
        ("Moderate", "high", "caution"),
        ("Moderate", "low", "go"),
        ("Poor", "high", "indoors"),
        ("Poor", "low", "caution"),
        ("Very Poor", "high", "indoors"),
        ("Very Poor", "low", "indoors"),
        ("Severe", "high", "indoors"),
        ("Severe", "low", "indoors"),
    ],
)
def test_every_regular_activity_table_cell(band: str, intensity: str, level: str) -> None:
    action = action_for("pe" if intensity == "high" else "assembly", intensity, band)

    assert action.level == level
    assert action.rule_id == f"SAANS-{band.upper().replace(' ', '-')}-{intensity.upper()}"
    assert action.text_en
    assert action.text_hi


@pytest.mark.parametrize(
    ("band", "level"),
    [
        ("Good", "go"),
        ("Satisfactory", "go"),
        ("Moderate", "caution"),
        ("Poor", "indoors"),
        ("Very Poor", "indoors"),
        ("Severe", "indoors"),
    ],
)
def test_every_sensitive_student_table_cell(band: str, level: str) -> None:
    action = action_for("sports", "high", band, sensitive=True)

    assert action.level == level
    assert action.rule_id == f"SAANS-{band.upper().replace(' ', '-')}-SENSITIVE"
    assert action.text_hi


def test_activity_name_is_reflected_in_regular_action() -> None:
    assert "recess" in action_for("recess", "low", "Poor").text_en


@pytest.mark.parametrize(
    ("intensity", "band"),
    [("medium", "Good"), ("high", "Hazardous")],
)
def test_invalid_rule_inputs_fail_loudly(intensity: str, band: str) -> None:
    with pytest.raises(ValueError):
        action_for("pe", intensity, band)


def test_very_poor_pa_system_text_only_for_assembly() -> None:
    from saans.rules import action_for
    pe = action_for("pe", "high", "Very Poor")
    assert pe.level == "indoors" and "assembly" not in pe.text_en and "PA system" not in pe.text_en and "असेंबली" not in pe.text_hi
    asm = action_for("assembly", "low", "Very Poor")
    assert asm.level == "indoors" and "PA system" in asm.text_en and "असेंबली" in asm.text_hi
