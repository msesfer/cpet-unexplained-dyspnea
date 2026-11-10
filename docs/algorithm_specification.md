# CPET Rule-Based Classification Algorithm

## 1. Purpose and provenance

This document describes the rule-based algorithm implemented in `src/classify_cpet.py` for the study:

*Diagnostic potential of cardiopulmonary exercise testing in unexplained dyspnoea and agreement of a rule-based algorithm: a single-centre retrospective study.*

The algorithm assigns CPET-defined physiological patterns using predefined clinical and physiological criteria. It operates independently of the laboratory's global CPET rating.

**Algorithm provenance**

- Analysis plan: Version 1.2, with post-analysis clarifications documented in version 1.3.
- Script: `classify_cpet.py`.
- Script approval/freeze date: 9 November 2026.
- Script SHA-256: `2b1e8081a179e9fb2b06d6669de4d8e08cfc5773fafcfc8114e884da9e4222d2`.
- Programming language: Python.
- Input format: REDCap raw (coded) CSV export.

Version 1.3 of the analysis plan documents implementation details and post-analysis clarifications. It did not introduce changes to the frozen classification thresholds or rules.

## 2. General principles

1. Every CPET is classified using a fixed, scripted algorithm.
2. Classification does not use the laboratory's global rating.
3. The same input data produce the same classification.
4. Specific physiological abnormalities may be identified at any exercise effort level, subject to the individual rule's requirements.
5. Normal and deconditioning classifications require at least intermediate effort.
6. Classification is based on CPET-defined patterns, not independently confirmed clinical diagnoses.
7. No thresholds were optimised against the study dataset.

## 3. Exercise effort classification

Effort is calculated from peak respiratory exchange ratio (RER) and the highest end-of-test Borg rating, defined as the higher of the dyspnoea and leg-effort ratings.

| Effort level | Definition | Rule |
|---|---|---|
| 1 | Adequate | RER ≥1.10 AND Borg ≥7 |
| 2 | Intermediate | Exactly one criterion is met |
| 3 | Submaximal | Neither criterion is met |

### Missing effort measurements

The implementation handles missing values as follows:

- Missing Borg: treated as the Borg criterion not met.
- Missing RER: effort level remains undefined.
- If RER is ≥1.10 and Borg is missing, effort is level 2.
- If RER is below 1.10 and Borg is missing, effort is level 3.

No RER or Borg values were missing in the final study cohort; therefore, this handling did not affect the reported results.

### Use of effort level in classification

| Pattern | Permitted effort |
|---|---|
| Cardiovascular: ischaemia, BP fall or qualifying arrhythmia | Any |
| Cardiovascular: O₂ pulse criterion | Levels 1 or 2 |
| Pulmonary vascular / ventilatory inefficiency | Any |
| Ventilatory limitation | Any |
| Exercise-induced desaturation | Any |
| Dysfunctional breathing | Any |
| Chronotropic incompetence | Level 1 only |
| Deconditioning | Levels 1 or 2 |
| Normal | Levels 1 or 2 |

A test with effort level 3 and no specific abnormal pattern is classified as not classifiable.

## 4. Specific physiological patterns

The algorithm evaluates six specific physiological patterns in a predefined priority order.

### 4.1 Cardiovascular limitation (code 3; priority 1)

The pattern is identified if at least one of the following criteria is met:

**A. Exercise-induced ischaemia**

- `ex_ischemia == 2`.

This variable represents exercise-induced ischaemic findings and is recorded separately from O₂ pulse abnormalities.

**B. Exercise-induced blood pressure fall**

- `bp_response == 3`.

**C. Exercise-induced arrhythmia**

Both conditions must be met:

- `ex_arrhythmia == 2`.
- `arrhythmia_type` is coded 3, 4 or 5.

The qualifying arrhythmias are:
- 3: Non-sustained ventricular tachycardia (NSVT).
- 4: Atrial fibrillation (AF).
- 5: Atrial flutter.

**D. Abnormal O₂ pulse trajectory**

All conditions must be met:

- O₂ pulse trajectory coded 2 or 3 (flattening or decline).
- Peak O₂ pulse below 80% predicted.
- Exercise effort level 1 or 2.

O₂ pulse flattening or decline alone is insufficient.

**Study findings:** Two patients were assigned a cardiovascular pattern, both triggered by an exercise-induced blood pressure fall. No patient met the ischaemia, arrhythmia or O₂ pulse criteria.

### 4.2 Pulmonary vascular / ventilatory inefficiency (code 5; priority 2)

Both criteria must be fulfilled:

- VE/VCO₂ slope >34.
- PETCO₂ at VT1 <33 mmHg.

The logical operator is AND, not OR.

No specific exercise effort level is required.

### 4.3 Ventilatory limitation (code 4; priority 3)

The criterion is:

- Breathing reserve at peak exercise <20%.

No specific exercise effort level is required.

### 4.4 Exercise-induced desaturation (code 7; priority 4)

Desaturation is identified if either of the following is met:

- SpO₂ falls by at least 4 percentage points from rest to the minimum exercise value, or
- Minimum exercise SpO₂ is <90%.

The resting and minimum exercise SpO₂ values are required to evaluate the corresponding fall criterion. A minimum SpO₂ below 90% can independently fulfil the second criterion.

No specific exercise effort level is required.

### 4.5 Dysfunctional breathing / hyperventilation (code 6; priority 5)

All of the following are required:

- A documented breathing pattern coded 2 or 3.
- Resting PETCO₂ <30 mmHg.
- PETCO₂ at VT1 ≥ resting PETCO₂.

Breathing pattern codes 2 and 3 represent the qualifying documented patterns in the REDCap coding.

A breathing pattern coded 9 (not described), or a missing breathing pattern, is not assessable and cannot fulfil this classification.

No specific exercise effort level is required.

### 4.6 Chronotropic incompetence (code 8; priority 6)

All of the following are required:

- Peak HR <85% of age-predicted maximum.
- Exercise effort level 1 (adequate).
- Confirmed absence of beta-blocker treatment.
- Confirmed absence of other rate-limiting medication.

Unknown medication status does not qualify as confirmed absence of rate-limiting medication.

Chronotropic incompetence is therefore not assessable when medication status is unknown or exercise effort is not level 1.

**Study findings:** The pattern was assessable in 6 patients and identified in 2, both as secondary patterns.

## 5. Primary and secondary classification

Specific patterns are evaluated in the following fixed priority order:

| Priority | Pattern | Code |
|---:|---|---:|
| 1 | Cardiovascular limitation | 3 |
| 2 | Pulmonary vascular / ventilatory inefficiency | 5 |
| 3 | Ventilatory limitation | 4 |
| 4 | Exercise-induced desaturation | 7 |
| 5 | Dysfunctional breathing | 6 |
| 6 | Chronotropic incompetence | 8 |

The algorithm assigns classifications according to the number of specific patterns identified:

| Number of specific patterns | Assignment |
|---:|---|
| 0 | Evaluate normal, deconditioning or not classifiable |
| 1 | One primary pattern |
| 2 | Highest-priority pattern as primary; next pattern as secondary |
| ≥3 | Mixed or other (code 9) as primary |

No patient in the final cohort was classified as mixed or other.

## 6. Normal and deconditioning classification

When no specific abnormal pattern is identified, the algorithm evaluates whether sufficient information and exercise effort are available.

### Essential variables

All five must be available:

- Peak VO₂ percentage predicted according to Wasserman.
- Exercise effort level.
- Breathing reserve.
- VE/VCO₂ slope.
- PETCO₂ at VT1.

If any of these are missing, the test is classified as not classifiable.

### Effort requirement

Normal and deconditioning classifications require effort level 1 or 2.

### Final assignment

If all essential data are available and effort is level 1 or 2:

- Peak VO₂ <80% predicted: Deconditioning (code 2).
- Peak VO₂ ≥80% predicted: Normal (code 1).

The threshold of 80% is therefore inclusive for normal classification and exclusive for deconditioning.

## 7. Not classifiable (code 10)

A test without a specific abnormal pattern is classified as not classifiable if:

- Exercise effort is level 3, or
- Any essential variable required for normal/deconditioning classification is missing.

The three unclassifiable tests in the final study cohort (records 15, 33 and 36) all had submaximal effort (level 3).

Tests with a specific physiological abnormality can retain that classification even if exercise effort is level 3, subject to the relevant pattern-specific effort requirements.

## 8. Missing data and assessability

### Required input columns

The script requires the following REDCap columns to be present:

- `record_id`
- `rer_peak`
- `borg_max`
- `vo2_peak_pct_wasserman`
- `ve_vco2_slope`
- `petco2_vt1`
- `petco2_rest`
- `br_pct`
- `hr_max_pct`
- `beta_blocker`
- `other_rate_limiting`
- `ex_ischemia`
- `bp_response`
- `ex_arrhythmia`
- `arrhythmia_type`
- `o2pulse_traj`
- `o2pulse_pct_pred`
- `spo2_rest`
- `spo2_min`
- `breath_pattern`

If a required column is absent, the script stops and reports the missing column names.

The presence of a column does not guarantee that every participant has a recorded value.

### Cardiovascular response data

The analysis plan specifies that cardiovascular response fields recorded as "not recorded" are treated as not detected for classification. This is a limitation because an abnormal cardiovascular response cannot be excluded when it was not documented.

### Pattern-specific assessability

- Desaturation: requires minimum exercise SpO₂ to be available; the fall criterion additionally requires resting SpO₂.
- Dysfunctional breathing: requires a documented breathing pattern coded 1, 2 or 3.
- Chronotropic incompetence: requires confirmed absence of beta-blocker and other rate-limiting medication and adequate effort.

In the final cohort, SpO₂ and breathing pattern were not recorded. Desaturation and dysfunctional breathing were therefore not assessable, rather than absent.

## 9. Primary study outcome

The primary outcome is the proportion of patients with a specific abnormal CPET pattern.

The outcome is defined as an algorithm-assigned primary classification code of:

- 3: Cardiovascular limitation.
- 4: Ventilatory limitation.
- 5: Pulmonary vascular / ventilatory inefficiency.
- 6: Dysfunctional breathing.
- 7: Exercise-induced desaturation.
- 8: Chronotropic incompetence.
- 9: Mixed or other.

The denominator is the complete cohort of 36 patients. Not-classifiable tests are counted as not having a specific abnormal pattern for this conservative primary estimate.

## 10. Output variables

The script generates the following output fields:

| Variable | Description |
|---|---|
| `record_id` | REDCap participant identifier |
| `effort_level` | Calculated effort category |
| `primary_code` | Primary classification code |
| `primary_pattern` | Primary classification label |
| `secondary_code` | Secondary classification code; 0 if none |
| `secondary_pattern` | Secondary classification label |
| `specific_patterns_met` | Semicolon-separated list of identified specific pattern codes |
| `n_specific` | Number of specific patterns identified |
| `specific_abnormal` | Whether the primary code is 3, 4, 5, 6, 7, 8 or 9 |
| `pattern_with_low_effort` | Indicates a specific pattern identified at effort level 3 |
| `desaturation_assessable` | Indicates whether minimum SpO₂ is available |
| `dysfunctional_breathing_assessable` | Indicates whether breathing pattern is coded 1, 2 or 3 |
| `chronotropic_assessable` | Indicates confirmed absence of rate-limiting drugs and effort level 1 |

## 11. Software testing

The original script contains 31 synthetic test cases covering:

- Effort classification and threshold boundaries.
- Peak VO₂ classification at 80%.
- Ventilatory inefficiency and breathing reserve thresholds.
- Cardiovascular triggers.
- O₂ pulse effort restrictions.
- Desaturation criteria.
- Dysfunctional breathing criteria.
- Chronotropic incompetence criteria.
- Priority assignment.
- Mixed classifications.
- Missing essential data.

The original script's built-in self-test reports 31/31 successful tests.

These tests establish expected software behaviour for the included synthetic scenarios. They do not constitute independent clinical validation of the algorithm.

## 12. Important interpretation and limitations

The algorithm identifies CPET-defined physiological patterns. These patterns are not independently confirmed diagnoses.

The laboratory's global CPET rating is not an input to the algorithm and is used only as an external comparator in the study's agreement analysis.

The classification is rule-based and does not incorporate clinical judgement or independent reader adjudication.

The algorithm should be interpreted in the context of:

- Small sample size and single-centre design.
- Frequently limited exercise effort.
- Incomplete physiological measurements.
- Incomplete cardiovascular response documentation.
- Lack of independent confirmation of identified patterns.

External validation in larger multicentre cohorts is required before broader clinical application.

## 13. Reproducibility

The frozen original script should be preserved without modification.

Future improvements, corrections or extensions should be developed as separately versioned files or releases, with a documented rationale and an explicit distinction from the algorithm used in the original study.
