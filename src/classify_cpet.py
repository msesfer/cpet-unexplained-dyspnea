"""
CPET pattern classification for the study "Diagnostic yield of CPET in patients
referred for unexplained dyspnea".

Implements section 6 of the analysis plan (v1.2, with the breathing reserve
threshold of < 20% from v1.1). Every parameter below is taken from the plan.
Nothing here is tuned to the data.

Usage:
    python classify_cpet.py --selftest                  # logic tests on made-up cases
    python classify_cpet.py RAW_EXPORT.csv OUTPUT.csv   # classify the real export

The script reads the REDCap RAW (coded) export. It never reads the laboratory's
global rating (lab_global_rating).

FREEZE: once approved, record the date in the plan sign-off line and do not edit.
"""
import sys
import numpy as np
import pandas as pd

# ----------------------------- PARAMETERS (plan section 5 and 6) -----------------------------
PARAMS = dict(
    rer_cut=1.10,            # effort: RER >= 1.10
    borg_cut=7,              # effort: highest end-of-test Borg >= 7
    vo2_pct_cut=80,          # peak VO2 < 80% predicted = reduced
    pct_pred_col="vo2_peak_pct_wasserman",
    ve_vco2_slope_cut=34,    # pulmonary vascular / inefficiency: slope > 34 ...
    petco2_vt1_cut=33,       # ... and PETCO2 at VT1 < 33 mmHg
    br_cut=20,               # ventilatory limitation: breathing reserve < 20%
    desat_drop=4,            # desaturation: SpO2 fall >= 4 points from rest ...
    desat_floor=90,          # ... or lowest SpO2 < 90%
    db_petco2_rest_cut=30,   # dysfunctional breathing: resting PETCO2 < 30 mmHg ...
    hr_max_pct_cut=85,       # chronotropic incompetence: peak HR < 85% of predicted max
    o2pulse_pct_cut=80,      # cardiovascular: O2 pulse flattening/decline with peak < 80% predicted
    effort_ok=(1, 2),        # effort levels allowed for Normal / Deconditioning / O2-pulse criterion
    chrono_effort=(1,),      # effort levels allowed for chronotropic incompetence
)

CODES = {1: "Normal", 2: "Deconditioning", 3: "Cardiovascular limitation",
         4: "Ventilatory limitation", 5: "Pulmonary vascular / ventilatory inefficiency",
         6: "Dysfunctional breathing", 7: "Exercise-induced desaturation",
         8: "Chronotropic incompetence", 9: "Mixed or other", 10: "Not classifiable"}
PRIORITY = [3, 5, 4, 7, 6, 8]   # priority order of the specific patterns (plan section 6)

REQUIRED = ["record_id", "rer_peak", "borg_max", "vo2_peak_pct_wasserman", "ve_vco2_slope",
            "petco2_vt1", "petco2_rest", "br_pct", "hr_max_pct", "beta_blocker",
            "other_rate_limiting", "ex_ischemia", "bp_response", "ex_arrhythmia",
            "arrhythmia_type", "o2pulse_traj", "o2pulse_pct_pred", "spo2_rest", "spo2_min",
            "breath_pattern"]


def compute_effort(df, p):
    """1 = RER and Borg criteria both met, 2 = one met, 3 = neither (same rule as REDCap)."""
    rer = df["rer_peak"] >= p["rer_cut"]
    borg = df["borg_max"] >= p["borg_cut"]          # NaN compares False
    lvl = np.where(rer & borg, 1, np.where(rer | borg, 2, 3))
    return pd.Series(np.where(df["rer_peak"].isna(), np.nan, lvl), index=df.index)


def classify(df, p=PARAMS):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df.copy()
    effort = compute_effort(df, p)
    pct = df[p["pct_pred_col"]]

    # ---------- specific patterns ----------
    cv_ischemia = df["ex_ischemia"] == 2
    cv_bpfall = df["bp_response"] == 3
    cv_arr = (df["ex_arrhythmia"] == 2) & df["arrhythmia_type"].isin([3, 4, 5])   # NSVT, AF, flutter
    cv_o2 = (df["o2pulse_traj"].isin([2, 3]) & (df["o2pulse_pct_pred"] < p["o2pulse_pct_cut"])
             & effort.isin(p["effort_ok"]))
    flags = {}
    flags[3] = cv_ischemia | cv_bpfall | cv_arr | cv_o2
    flags[5] = (df["ve_vco2_slope"] > p["ve_vco2_slope_cut"]) & (df["petco2_vt1"] < p["petco2_vt1_cut"])
    flags[4] = df["br_pct"] < p["br_cut"]

    desat_assessable = df["spo2_min"].notna()
    both = df["spo2_rest"].notna() & df["spo2_min"].notna()
    flags[7] = desat_assessable & (((df["spo2_rest"] - df["spo2_min"]) >= p["desat_drop"]) & both
                                   | (df["spo2_min"] < p["desat_floor"]))

    db_assessable = df["breath_pattern"].isin([1, 2, 3])        # 9 (not described) or blank = not assessable
    flags[6] = (db_assessable & df["breath_pattern"].isin([2, 3])
                & (df["petco2_rest"] < p["db_petco2_rest_cut"])
                & (df["petco2_vt1"] >= df["petco2_rest"]))

    on_drug = (df["beta_blocker"] == 1) | (df["other_rate_limiting"] == 1)
    drug_known = (df["beta_blocker"] == 0) & (df["other_rate_limiting"] == 0)
    chrono_assessable = drug_known & effort.isin(p["chrono_effort"])
    flags[8] = chrono_assessable & (df["hr_max_pct"] < p["hr_max_pct_cut"])

    spec = pd.DataFrame({c: flags[c].fillna(False).astype(bool) for c in PRIORITY})
    n_spec = spec.sum(axis=1)

    # ---------- essential data for Normal / Deconditioning ----------
    essential_missing = (pct.isna() | effort.isna() | df["br_pct"].isna()
                         | df["ve_vco2_slope"].isna() | df["petco2_vt1"].isna())

    primary, secondary, listed = [], [], []
    for i in df.index:
        met = [c for c in PRIORITY if spec.at[i, c]]
        listed.append(";".join(str(c) for c in met))
        if len(met) >= 3:
            primary.append(9); secondary.append(0)
        elif len(met) >= 1:
            primary.append(met[0]); secondary.append(met[1] if len(met) == 2 else 0)
        else:
            secondary.append(0)
            if essential_missing[i] or effort[i] not in p["effort_ok"]:
                primary.append(10)
            else:
                primary.append(2 if pct[i] < p["vo2_pct_cut"] else 1)

    out = pd.DataFrame({
        "record_id": df["record_id"],
        "effort_level": effort,
        "primary_code": primary,
        "primary_pattern": [CODES[c] for c in primary],
        "secondary_code": secondary,
        "secondary_pattern": ["None" if c == 0 else CODES[c] for c in secondary],
        "specific_patterns_met": listed,
        "n_specific": n_spec,
        "specific_abnormal": [c in (3, 4, 5, 6, 7, 8, 9) for c in primary],
        "pattern_with_low_effort": (effort == 3) & (n_spec > 0),
        "desaturation_assessable": desat_assessable,
        "dysfunctional_breathing_assessable": db_assessable,
        "chronotropic_assessable": chrono_assessable,
    })
    return out


# ----------------------------- SELF-TEST (made-up cases only) -----------------------------
def _base():
    return dict(record_id=0, rer_peak=1.15, borg_max=8, vo2_peak_pct_wasserman=100, ve_vco2_slope=28,
                petco2_vt1=36, petco2_rest=33, br_pct=40, hr_max_pct=90, beta_blocker=0,
                other_rate_limiting=0, ex_ischemia=1, bp_response=1, ex_arrhythmia=1,
                arrhythmia_type=np.nan, o2pulse_traj=1, o2pulse_pct_pred=100, spo2_rest=np.nan,
                spo2_min=np.nan, breath_pattern=9)


def selftest():
    cases = [
        ("normal, adequate effort", {}, 1, 0),
        ("VO2 exactly 80% is normal", dict(vo2_peak_pct_wasserman=80), 1, 0),
        ("VO2 79% is deconditioning", dict(vo2_peak_pct_wasserman=79), 2, 0),
        ("RER 1.10 and Borg 7 exactly = effort 1, normal", dict(rer_peak=1.10, borg_max=7), 1, 0),
        ("intermediate effort, reduced VO2 -> deconditioning", dict(rer_peak=1.05, vo2_peak_pct_wasserman=70), 2, 0),
        ("submaximal, no specific pattern -> not classifiable", dict(rer_peak=0.95, borg_max=5), 10, 0),
        ("submaximal with inefficiency pattern -> pattern kept", dict(rer_peak=0.95, borg_max=5, ve_vco2_slope=40, petco2_vt1=30), 5, 0),
        ("slope exactly 34 is not abnormal", dict(ve_vco2_slope=34, petco2_vt1=30), 1, 0),
        ("breathing reserve 19% -> ventilatory", dict(br_pct=19), 4, 0),
        ("breathing reserve exactly 20% -> not ventilatory", dict(br_pct=20), 1, 0),
        ("ischemia -> cardiovascular", dict(ex_ischemia=2), 3, 0),
        ("BP fall -> cardiovascular", dict(bp_response=3), 3, 0),
        ("ventricular ectopy alone is not cardiovascular", dict(ex_arrhythmia=2, arrhythmia_type=1), 1, 0),
        ("NSVT -> cardiovascular", dict(ex_arrhythmia=2, arrhythmia_type=3), 3, 0),
        ("O2 pulse flattening, <80% pred, effort 2 -> cardiovascular", dict(rer_peak=1.05, o2pulse_traj=2, o2pulse_pct_pred=70), 3, 0),
        ("O2 pulse flattening but 85% pred -> not cardiovascular", dict(o2pulse_traj=2, o2pulse_pct_pred=85), 1, 0),
        ("O2 pulse flattening at effort 3 -> not cardiovascular", dict(rer_peak=0.95, borg_max=5, o2pulse_traj=2, o2pulse_pct_pred=70), 10, 0),
        ("desaturation by 4-point fall", dict(spo2_rest=97, spo2_min=93), 7, 0),
        ("desaturation by SpO2 < 90", dict(spo2_rest=94, spo2_min=89), 7, 0),
        ("3-point fall is not desaturation", dict(spo2_rest=97, spo2_min=94), 1, 0),
        ("dysfunctional breathing", dict(breath_pattern=3, petco2_rest=28, petco2_vt1=32), 6, 0),
        ("breathing not described -> never dysfunctional breathing", dict(breath_pattern=9, petco2_rest=28, petco2_vt1=32), 1, 0),
        ("chronotropic incompetence, effort 1, no drugs", dict(hr_max_pct=80), 8, 0),
        ("peak HR 85% is not chronotropic", dict(hr_max_pct=85), 1, 0),
        ("on beta-blocker -> not chronotropic", dict(hr_max_pct=80, beta_blocker=1), 1, 0),
        ("other rate-limiting drug -> not chronotropic", dict(hr_max_pct=80, other_rate_limiting=1), 1, 0),
        ("effort 2 -> not chronotropic", dict(hr_max_pct=80, rer_peak=1.05), 1, 0),
        ("two patterns: cardiovascular primary, ventilatory secondary", dict(ex_ischemia=2, br_pct=15), 3, 4),
        ("priority: inefficiency before ventilatory", dict(ve_vco2_slope=40, petco2_vt1=30, br_pct=15), 5, 4),
        ("three patterns -> mixed", dict(ex_ischemia=2, br_pct=15, ve_vco2_slope=40, petco2_vt1=30), 9, 0),
        ("essential data missing -> not classifiable", dict(vo2_peak_pct_wasserman=np.nan), 10, 0),
    ]
    rows = []
    for i, (_, over, _, _) in enumerate(cases):
        d = _base(); d.update(over); d["record_id"] = i; rows.append(d)
    res = classify(pd.DataFrame(rows))
    fails = 0
    for i, (name, _, exp_p, exp_s) in enumerate(cases):
        got_p, got_s = int(res.at[i, "primary_code"]), int(res.at[i, "secondary_code"])
        ok = (got_p, got_s) == (exp_p, exp_s)
        fails += not ok
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  expected {exp_p}/{exp_s}, got {got_p}/{got_s}"))
    print(f"\n{len(cases) - fails}/{len(cases)} tests passed")
    return fails == 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if len(sys.argv) != 3:
        sys.exit("Usage: python classify_cpet.py RAW_EXPORT.csv OUTPUT.csv  |  --selftest")
    raw = pd.read_csv(sys.argv[1])
    out = classify(raw)
    # Safety check: effort level must match the value calculated by REDCap
    if "effort_level" in raw.columns and not (raw["effort_level"].fillna(-1).values == out["effort_level"].fillna(-1).values).all():
        print("WARNING: effort level differs from the REDCap-calculated field. Check RER and Borg entries.")
    out.to_csv(sys.argv[2], index=False)
    print(out["primary_pattern"].value_counts().to_string())
    print(f"\nSaved {len(out)} rows to {sys.argv[2]}")
