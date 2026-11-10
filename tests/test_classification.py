"""Regression tests for the frozen CPET classification algorithm.

Run from the repository root:
    python -m pytest -q

The tests import the existing implementation from src/classify_cpet.py.
They do not modify the frozen classification script or use patient data.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from classify_cpet import REQUIRED, classify, compute_effort  # noqa: E402


def base_case(**overrides):
    """Synthetic, otherwise normal CPET with adequate effort."""
    row = dict(
        record_id="SYNTHETIC",
        rer_peak=1.15,
        borg_max=8,
        vo2_peak_pct_wasserman=100,
        ve_vco2_slope=28,
        petco2_vt1=36,
        petco2_rest=33,
        br_pct=40,
        hr_max_pct=90,
        beta_blocker=0,
        other_rate_limiting=0,
        ex_ischemia=1,
        bp_response=1,
        ex_arrhythmia=1,
        arrhythmia_type=np.nan,
        o2pulse_traj=1,
        o2pulse_pct_pred=100,
        spo2_rest=np.nan,
        spo2_min=np.nan,
        breath_pattern=9,
    )
    row.update(overrides)
    return row


def run_one(**overrides):
    return classify(pd.DataFrame([base_case(**overrides)])).iloc[0]


def test_required_columns_are_enforced():
    frame = pd.DataFrame([base_case()]).drop(columns=["rer_peak"])
    with pytest.raises(ValueError, match="Missing columns"):
        classify(frame)


@pytest.mark.parametrize(
    "rer,borg,expected",
    [
        (1.10, 7, 1),
        (1.10, 6, 2),
        (1.09, 7, 2),
        (1.09, 6, 3),
    ],
)
def test_effort_boundaries(rer, borg, expected):
    effort = compute_effort(pd.DataFrame([base_case(rer_peak=rer, borg_max=borg)]),
                            {"rer_cut": 1.10, "borg_cut": 7})
    assert effort.iloc[0] == expected


def test_missing_borg_counts_as_borg_criterion_not_met():
    frame = pd.DataFrame([base_case(borg_max=np.nan)])
    assert compute_effort(frame, {"rer_cut": 1.10, "borg_cut": 7}).iloc[0] == 2


def test_missing_rer_makes_effort_undefined_even_if_borg_is_high():
    frame = pd.DataFrame([base_case(rer_peak=np.nan, borg_max=9)])
    assert pd.isna(compute_effort(frame, {"rer_cut": 1.10, "borg_cut": 7}).iloc[0])
    result = run_one(rer_peak=np.nan, borg_max=9)
    assert result.primary_code == 10


def test_vo2_cutoff_is_strictly_below_80_for_deconditioning():
    assert run_one(vo2_peak_pct_wasserman=79.99).primary_code == 2
    assert run_one(vo2_peak_pct_wasserman=80).primary_code == 1


def test_intermediate_effort_allows_normal_and_deconditioning():
    assert run_one(rer_peak=1.05, borg_max=8, vo2_peak_pct_wasserman=70).primary_code == 2
    assert run_one(rer_peak=1.05, borg_max=8, vo2_peak_pct_wasserman=100).primary_code == 1


def test_submaximal_effort_without_specific_pattern_is_unclassifiable():
    result = run_one(rer_peak=0.95, borg_max=5)
    assert result.effort_level == 3
    assert result.primary_code == 10


def test_specific_pattern_is_retained_despite_submaximal_effort():
    result = run_one(rer_peak=0.95, borg_max=5, bp_response=3)
    assert result.primary_code == 3
    assert bool(result.pattern_with_low_effort)


@pytest.mark.parametrize(
    "changes,expected",
    [
        ({"ex_ischemia": 2}, 3),
        ({"bp_response": 3}, 3),
        ({"ex_arrhythmia": 2, "arrhythmia_type": 3}, 3),  # NSVT
        ({"ex_arrhythmia": 2, "arrhythmia_type": 4}, 3),  # AF
        ({"ex_arrhythmia": 2, "arrhythmia_type": 5}, 3),  # flutter
        ({"ex_arrhythmia": 2, "arrhythmia_type": 1}, 1),  # non-qualifying type
    ],
)
def test_cardiovascular_triggers(changes, expected):
    assert run_one(**changes).primary_code == expected


def test_o2_pulse_requires_trajectory_low_peak_and_effort_1_or_2():
    assert run_one(o2pulse_traj=2, o2pulse_pct_pred=79.9).primary_code == 3
    assert run_one(o2pulse_traj=2, o2pulse_pct_pred=80).primary_code == 1
    assert run_one(o2pulse_traj=2, o2pulse_pct_pred=70,
                   rer_peak=0.95, borg_max=5).primary_code == 10


def test_pulmonary_vascular_inefficiency_requires_both_criteria():
    assert run_one(ve_vco2_slope=34.01, petco2_vt1=32.9).primary_code == 5
    assert run_one(ve_vco2_slope=34, petco2_vt1=30).primary_code == 1
    assert run_one(ve_vco2_slope=40, petco2_vt1=33).primary_code == 1


def test_ventilatory_limitation_cutoff_is_strictly_below_20():
    assert run_one(br_pct=19.99).primary_code == 4
    assert run_one(br_pct=20).primary_code == 1


def test_desaturation_uses_four_point_fall_or_minimum_below_90():
    assert run_one(spo2_rest=97, spo2_min=93).primary_code == 7
    assert run_one(spo2_rest=94, spo2_min=89).primary_code == 7
    assert run_one(spo2_rest=97, spo2_min=94).primary_code == 1
    assert run_one(spo2_rest=np.nan, spo2_min=89).primary_code == 7


def test_desaturation_assessability_requires_minimum_spo2():
    result = run_one(spo2_rest=97, spo2_min=np.nan)
    assert not bool(result.desaturation_assessable)


def test_dysfunctional_breathing_requires_all_three_conditions():
    assert run_one(breath_pattern=3, petco2_rest=29.9, petco2_vt1=29.9).primary_code == 6
    assert run_one(breath_pattern=3, petco2_rest=30, petco2_vt1=32).primary_code == 1
    assert run_one(breath_pattern=3, petco2_rest=28, petco2_vt1=27).primary_code == 1
    assert run_one(breath_pattern=9, petco2_rest=28, petco2_vt1=32).primary_code == 1


def test_dysfunctional_breathing_assessability_uses_documented_pattern_codes():
    assert bool(run_one(breath_pattern=1).dysfunctional_breathing_assessable)
    assert bool(run_one(breath_pattern=2).dysfunctional_breathing_assessable)
    assert bool(run_one(breath_pattern=3).dysfunctional_breathing_assessable)
    assert not bool(run_one(breath_pattern=9).dysfunctional_breathing_assessable)
    assert not bool(run_one(breath_pattern=np.nan).dysfunctional_breathing_assessable)


def test_chronotropic_incompetence_requires_adequate_effort_and_no_rate_limiting_drugs():
    assert run_one(hr_max_pct=84.9).primary_code == 8
    assert run_one(hr_max_pct=85).primary_code == 1
    assert run_one(hr_max_pct=80, beta_blocker=1).primary_code == 1
    assert run_one(hr_max_pct=80, other_rate_limiting=1).primary_code == 1
    assert run_one(hr_max_pct=80, rer_peak=1.05, borg_max=8).primary_code == 1


def test_chronotropic_assessability_requires_known_absence_of_both_drug_types_and_effort_1():
    assert bool(run_one(hr_max_pct=90).chronotropic_assessable)
    assert not bool(run_one(beta_blocker=np.nan).chronotropic_assessable)
    assert not bool(run_one(other_rate_limiting=np.nan).chronotropic_assessable)
    assert not bool(run_one(rer_peak=1.05, borg_max=8).chronotropic_assessable)


def test_two_patterns_follow_priority_and_assign_secondary():
    result = run_one(ex_ischemia=2, br_pct=15)
    assert result.primary_code == 3
    assert result.secondary_code == 4
    assert result.specific_patterns_met == "3;4"


def test_pulmonary_vascular_pattern_precedes_ventilatory_pattern():
    result = run_one(ve_vco2_slope=40, petco2_vt1=30, br_pct=15)
    assert result.primary_code == 5
    assert result.secondary_code == 4
    assert result.specific_patterns_met == "5;4"


def test_three_or_more_patterns_are_mixed_or_other():
    result = run_one(ex_ischemia=2, br_pct=15, ve_vco2_slope=40, petco2_vt1=30)
    assert result.primary_code == 9
    assert result.secondary_code == 0
    assert result.n_specific == 3


@pytest.mark.parametrize(
    "missing_column",
    ["vo2_peak_pct_wasserman", "br_pct", "ve_vco2_slope", "petco2_vt1"],
)
def test_missing_essential_data_prevents_normal_or_deconditioning(missing_column):
    result = run_one(**{missing_column: np.nan})
    assert result.primary_code == 10


def test_missing_nonessential_data_does_not_prevent_normal_classification():
    result = run_one(
        petco2_rest=np.nan,
        hr_max_pct=np.nan,
        beta_blocker=np.nan,
        other_rate_limiting=np.nan,
        ex_ischemia=np.nan,
        bp_response=np.nan,
        ex_arrhythmia=np.nan,
        arrhythmia_type=np.nan,
        o2pulse_traj=np.nan,
        o2pulse_pct_pred=np.nan,
        spo2_rest=np.nan,
        spo2_min=np.nan,
        breath_pattern=np.nan,
    )
    assert result.primary_code == 1


def test_specific_pattern_flags_are_not_suppressed_by_missing_effort():
    result = run_one(rer_peak=np.nan, bp_response=3)
    assert result.primary_code == 3
    assert pd.isna(result.effort_level)
