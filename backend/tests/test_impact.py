"""Impact estimate: exposure avoided by suggested (non-optional) swaps."""
import pytest

from saans.models import Period, School
from saans.planner import plan_day, plan_week


def _row(h, pm, day="2026-10-09"):
    return {"time": f"{day}T{h:02d}:00", "pm25": pm, "pm10": pm, "pm25_cal": pm, "pm10_cal": pm}


def _school(students=40):
    t = lambda i, s, e, typ, inten, out: Period(id=i, label=i, start=s, end=e, type=typ, intensity=inten, outdoor=out, swappable=True)
    return School(id="z", name="Z", city="D", lat=0, lon=0, students_per_class=students,
                  timetable=[t("pe", "08:40", "09:20", "pe", "high", True), t("c8", "13:40", "14:20", "class", "low", False)])


def test_default_students_per_class() -> None:
    assert School(id="a", name="A", city="C", lat=0, lon=0, timetable=[]).students_per_class == 40


def test_per_swap_impact_arithmetic() -> None:
    plan = plan_day(_school(), [_row(8, 200), _row(9, 200), _row(13, 40), _row(14, 40)], "2026-10-09")
    sw = plan.periods[0].swap
    assert sw and not sw.optional
    im = sw.impact
    assert im.pm25_before == 200 and im.pm25_after == 40 and im.reduction_pct == 80
    assert im.minutes == 40 and im.students == 40
    assert im.exposure_avoided == pytest.approx(160 * (40 / 60) * 40, rel=1e-3)   # µg/m³·h × students
    assert im.band_from == "Very Poor" and im.band_to == "Satisfactory"
    day = plan.impact
    assert day.swaps == 1 and day.students_moved == 40 and day.minutes == 40
    assert day.student_hours_out_of_poor == pytest.approx(40 * 40 / 60, rel=1e-3)
    assert day.exposure_avoided == pytest.approx(im.exposure_avoided)
    assert day.reduction_pct == 80 and day.worst_band_from == "Very Poor"


def test_students_per_class_scales_exposure() -> None:
    a = plan_day(_school(40), [_row(8, 200), _row(9, 200), _row(13, 40), _row(14, 40)], "2026-10-09").impact
    b = plan_day(_school(20), [_row(8, 200), _row(9, 200), _row(13, 40), _row(14, 40)], "2026-10-09").impact
    assert b.exposure_avoided == pytest.approx(a.exposure_avoided / 2, rel=1e-3)


def test_optional_swaps_do_not_count() -> None:
    # PE in Moderate (caution) with a Good slot -> optional swap; impact must stay zero
    plan = plan_day(_school(), [_row(8, 80), _row(9, 80), _row(13, 10), _row(14, 10)], "2026-10-09")
    assert plan.periods[0].swap and plan.periods[0].swap.optional
    assert plan.impact.swaps == 0 and plan.impact.students_moved == 0 and plan.impact.exposure_avoided == 0


def test_swap_into_poor_air_counts_exposure_but_not_hours_out_of_poor() -> None:
    # Low-intensity recess in Very Poor air may swap into a Poor hour (caution): exposure drops, but the
    # students are not "out of Poor/Very Poor air", so those student-hours must not be counted.
    t = lambda i, s_, e, typ, inten, out: Period(id=i, label=i, start=s_, end=e, type=typ, intensity=inten, outdoor=out, swappable=True)
    s = School(id="z", name="Z", city="D", lat=0, lon=0, timetable=[t("rec", "10:40", "11:00", "recess", "low", True), t("c", "13:40", "14:20", "class", "low", False)])
    plan = plan_day(s, [_row(10, 200), _row(13, 100), _row(14, 100)], "2026-10-09")
    sw = plan.periods[0].swap
    assert sw and sw.impact.band_to == "Poor"
    assert plan.impact.exposure_avoided > 0 and plan.impact.student_hours_out_of_poor == 0


def test_replay_day_impact() -> None:
    from saans.sources import load_replay
    from saans.store import SEED_SCHOOLS
    rows, day = load_replay("delhi-nov")
    im = plan_day(SEED_SCHOOLS[0], rows, day, replay_date=day).impact
    assert im.swaps == 1 and im.students_moved == 40 and im.minutes == 40 and im.worst_band_from == "Very Poor"
    assert 40 <= im.reduction_pct <= 90 and im.student_hours_out_of_poor == pytest.approx(40 * 40 / 60, rel=1e-3)


def test_week_totals_sum_days() -> None:
    rows = [_row(h, 200 if h in (8, 9) else 40, d) for d in ("2026-10-09", "2026-10-10") for h in range(24)]
    week = plan_week(_school(), rows)
    assert len(week["days"]) == 2
    total = week["impact"]
    assert total["swaps"] == sum(d["impact"]["swaps"] for d in week["days"]) == 2
    assert total["exposure_avoided"] == pytest.approx(sum(d["impact"]["exposure_avoided"] for d in week["days"]))
    assert total["student_hours_out_of_poor"] == pytest.approx(2 * 40 * 40 / 60, rel=1e-3)
