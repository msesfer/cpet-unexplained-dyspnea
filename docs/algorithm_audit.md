# CPET Classification Algorithm: Implementation Audit

## 1. Purpose

This document records the reconciliation of the frozen Python classification algorithm (`classify_cpet.py`) against the study analysis plan, final abstract and REDCap data dictionary.

The purpose is to establish the correspondence between the prespecified classification rules and their software implementation, identify implementation details clarified after analysis, and preserve the provenance of the algorithm used to generate the study results.

## 2. Documents reviewed

The audit was based on:

1. Analysis plan: *Diagnostic yield of CPET in patients referred for unexplained dyspnea*, version 1.3, dated 10 November 2026.
2. Frozen Python implementation: `classify_cpet.py`.
3. REDCap data dictionary, version 2.
4. Final study abstract.
5. Post-analysis clarifications supplied by the study team.

The study team confirmed that the REDCap ischaemia variable (`ex_ischemia`) was recorded separately from O₂ pulse trajectory (`o2pulse_traj`).

## 3. Algorithm provenance

The analysis plan documents the frozen script as:

- File: `classify_cpet.py`
- Approval/freeze date: 9 November 2026
- SHA-256: `2b1e8081a179e9fb2b06d6669de4d8e08cfc5773fafcfc8114e884da9e4222d2`

The SHA-256 fingerprint of the reviewed Python file matches the fingerprint recorded in section 13 of analysis plan version 1.3.

The plan states that no threshold or classification rule was changed after the script was frozen.

Version 1.3 documents post-analysis clarifications and additional descriptive analyses. It does not represent a revised classification algorithm.

## 4. Reconciliation of classification rules

| Component | Analysis plan | Python implementation | Audit conclusion |
|---|---|---|---|
| Exercise effort | RER ≥1.10 and Borg ≥7; intermediate if one criterion met; submaximal if neither met | Implemented using `compute_effort()` | Concordant |
| Cardiovascular: ischaemia | Exercise-induced ischaemia | `ex_ischemia == 2` | Concordant |
| Cardiovascular: BP | Exercise-induced BP fall | `bp_response == 3` | Concordant |
| Cardiovascular: arrhythmia | NSVT, new AF or flutter | Arrhythmia code 2 and type 3, 4 or 5 | Concordant |
| Cardiovascular: O₂ pulse | Early flattening or decline, peak O₂ pulse <80% predicted, effort 1–2 | Implemented using trajectory, predicted percentage and effort | Concordant |
| Pulmonary vascular / ventilatory inefficiency | VE/VCO₂ slope >34 AND PETCO₂ at VT1 <33 mmHg | Both conditions required | Concordant |
| Ventilatory limitation | Breathing reserve <20% | `br_pct < 20` | Concordant |
| Desaturation | SpO₂ fall ≥4 points OR minimum SpO₂ <90% | Both alternatives implemented | Concordant |
| Dysfunctional breathing | Documented qualifying pattern, resting PETCO₂ <30 mmHg and PETCO₂ at VT1 ≥ resting value | All criteria implemented | Concordant |
| Chronotropic incompetence | Peak HR <85%, effort 1, no beta-blocker or other rate-limiting drug | All conditions implemented | Concordant |
| Deconditioning | Peak VO₂ <80% predicted, effort 1–2 and no specific pattern | Implemented | Concordant |
| Normal | Peak VO₂ ≥80% predicted, effort 1–2 and no specific pattern | Implemented | Concordant |
| Multiple patterns | Priority order; secondary pattern when two; mixed if ≥3 | Implemented | Concordant |
| Not classifiable | Effort level 3 without a specific pattern or missing essential data | Implemented | Concordant |

## 5. Specific implementation clarifications

### 5.1 O₂ pulse and cardiovascular classification

The cardiovascular pattern includes four alternative triggers:

- Exercise-induced ischaemia.
- Exercise-induced BP fall.
- Qualifying exercise-induced arrhythmia.
- Early O₂ pulse flattening or decline with peak O₂ pulse below 80% predicted and effort level 1 or 2.

The REDCap ischaemia variable is separate from O₂ pulse trajectory.

In the final cohort, both cardiovascular classifications were triggered by exercise-induced BP fall.

No patient met the ischaemia, qualifying arrhythmia or O₂ pulse criteria.

Record 20 showed O₂ pulse flattening but had submaximal effort. It was therefore excluded by the O₂ pulse effort restriction.

### 5.2 Missing RER and Borg

The implementation handles missing effort measurements asymmetrically:

- Missing Borg is treated as the Borg criterion not met.
- Missing RER leaves the calculated effort level undefined.

This behaviour is documented in analysis plan version 1.3.

No RER or Borg value was missing in the final study dataset. This implementation detail did not affect the reported results.

### 5.3 Not-classifiable tests

Three tests were classified as not classifiable:

- Record 15.
- Record 33.
- Record 36.

All three had effort level 3 and no specific abnormal physiological pattern.

### 5.4 Chronotropic incompetence

Chronotropic incompetence required:

- Peak HR below 85% of age-predicted maximum.
- Adequate effort (level 1).
- Confirmed absence of beta-blocker and other rate-limiting medication.

Unknown medication status was not treated as confirmed absence.

The pattern was assessable in six patients and identified in two, both as secondary patterns.

### 5.5 Patterns not assessable

SpO₂ and breathing pattern were not recorded in the study dataset.

Consequently:

- Exercise-induced desaturation was not assessable.
- Dysfunctional breathing was not assessable.

These patterns must not be interpreted as absent.

### 5.6 Multiple-pattern assignment

The algorithm uses a fixed priority hierarchy.

- One specific pattern: primary classification.
- Two specific patterns: primary and secondary classifications.
- Three or more specific patterns: mixed or other.

No patient in the final cohort was classified as mixed or other.

## 6. Verification of software behaviour

The original script contains 31 synthetic test cases covering threshold boundaries, specific classification rules, missing essential data and priority assignment.

The built-in self-test was executed on the reviewed script:

**31/31 synthetic tests passed.**

This verifies that the implementation produces the expected outputs for the included synthetic scenarios. It does not independently validate the clinical appropriateness of the criteria or establish diagnostic accuracy.

## 7. Study results relevant to the audit

The algorithm identified a specific abnormal pattern in 9 of 36 tests.

The primary patterns were:

| Pattern | Number |
|---|---:|
| Pulmonary vascular / ventilatory inefficiency | 4 |
| Ventilatory limitation | 3 |
| Cardiovascular limitation | 2 |
| Total | 9 |

Other classifications:

| Classification | Number |
|---|---:|
| Normal | 16 |
| Deconditioning | 8 |
| Not classifiable | 3 |

Chronotropic incompetence was identified in two patients as a secondary pattern and therefore does not appear in the primary-pattern distribution above.

The laboratory global rating was not used by the algorithm. Agreement analyses against the laboratory rating were conducted separately and were documented as post hoc descriptive analyses in version 1.3 of the analysis plan.

## 8. Post hoc analyses

The following analyses were added after the original plan was signed:

- Sensitivity and specificity of the script against the laboratory global rating.
- Positive and negative predictive values.
- Cohen's kappa.
- Description of the nine patients with a specific physiological pattern.
- Exploratory correlation of BMI with peak VO₂, both absolute and weight-indexed.

These analyses are descriptive and should be identified as post hoc.

The laboratory global rating is a comparator, not an independent diagnostic gold standard.

## 9. Final audit conclusion

The reviewed frozen Python script is concordant with the classification rules documented in analysis plan versions 1.2 and 1.3.

The apparent differences identified during the initial code review were resolved by reference to the full analysis plan and post-analysis clarifications.

The following points were confirmed:

- O₂ pulse is part of the cardiovascular definition and is subject to an effort restriction.
- The REDCap ischaemia variable is recorded separately from O₂ pulse trajectory.
- Missing RER and Borg values are handled differently, without impact on the final cohort.
- The three unclassifiable tests were all due to submaximal effort.
- Chronotropic incompetence was assessable in six patients and identified in two as a secondary pattern.
- Desaturation and dysfunctional breathing were not assessable because the relevant measurements were unavailable.

No changes to the frozen classification script are indicated by this documentation review.

The original script should be preserved as the implementation used for the study. Any future modifications should be separately versioned and documented.

## 10. Audit status and sign-off

**Technical review:** Completed against the available source documents and study-team clarifications.

**Independent clinical validation:** Not performed.

**External validation:** Pending future research.


