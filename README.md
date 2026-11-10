# Diagnostic potential of cardiopulmonary exercise testing in unexplained dyspnoea and agreement of a rule-based algorithm

**A single-centre retrospective study**

## 1. Study overview

This repository contains the research documentation and Python code developed for the study:

*Diagnostic potential of cardiopulmonary exercise testing in unexplained dyspnoea and agreement of a rule-based algorithm: a single-centre retrospective study.*

Unexplained dyspnoea is a complex clinical presentation with potentially multiple underlying causes. Cardiopulmonary exercise testing (CPET) is recommended in the evaluation of unexplained dyspnoea by ATS/ACCP (2003), AHA (2010) and ERS (2007) statements.

However, interpretation of abnormal physiological patterns remains challenging, particularly in patients with submaximal exercise effort or preserved peak oxygen uptake (VO₂).

This study evaluates the diagnostic potential of CPET in patients referred for unexplained dyspnoea and investigates the agreement between a pre-specified rule-based classification algorithm and the laboratory's global CPET rating.

## 2. Study objectives

The primary objectives are to:

- Estimate the proportion of patients in whom CPET identifies a specific physiological abnormality.
- Describe the distribution of physiological patterns identified by CPET.
- Compare the classification provided by a pre-specified rule-based algorithm with the laboratory's global normal/abnormal rating.
- Explore potential discrepancies between algorithmic classification and routine laboratory interpretation, particularly in patients with preserved peak VO₂.

## 3. Study design and population

- **Design:** Retrospective, single-centre observational study.
- **Population:** 36 adults referred to the Department of Cardiology.
- **Main presenting symptom:** Unexplained dyspnoea.
- **Echocardiography:** Normal in 27 patients; unavailable in 9 patients.
- **Sex distribution:** 86% women.
- **Median age:** 64 years (IQR 54–69 years).

All participants underwent their first CPET.

## 4. CPET classification algorithm

A pre-specified, scripted rule-based algorithm was developed to assign one primary physiological pattern based on predefined CPET criteria.

### 4.1 Classification categories

The algorithm assigns one of the following primary classifications:

1. Cardiovascular limitation.
2. Ventilatory limitation.
3. Pulmonary vascular / ventilatory inefficiency.
4. Chronotropic incompetence.
5. Deconditioning.
6. Normal CPET.
7. Unclassifiable.

### 4.2 Physiological criteria

| Classification | Pre-specified criteria |
|---|---|
| Cardiovascular | Exercise-induced blood pressure fall, ischaemia or arrhythmia |
| Ventilatory limitation | Breathing reserve <20% |
| Pulmonary vascular / ventilatory inefficiency | VE/VCO₂ slope >34 and PETCO₂ at VT1 <33 mmHg |
| Chronotropic incompetence | Criteria defined in the classification script |
| Deconditioning | Peak VO₂ <80% of Wasserman-predicted |
| Normal | No specific abnormality identified and sufficient exercise effort |

### 4.3 Exercise effort assessment

Exercise effort was graded according to peak respiratory exchange ratio (RER) and maximum Borg score:

- **Adequate effort:** Peak RER ≥1.10 and Borg score ≥7.
- **Intermediate effort:** One of the two criteria was met.
- **Submaximal effort:** Neither criterion was met.

Normal and deconditioning classifications required at least intermediate effort.

Tests with insufficient effort and no assignable specific physiological abnormality could be classified as unclassifiable.

### 4.4 Comparison with laboratory assessment

The algorithm's classification was compared with the laboratory's global CPET rating (normal or abnormal).

The laboratory rating was used as a comparator rather than an independent diagnostic gold standard.

The analysis specifically examined cases in which the algorithm identified physiological abnormalities despite a normal laboratory global rating.

## 5. Statistical analysis

The statistical analysis included:

- Descriptive statistics for demographic and CPET characteristics.
- Frequency and distribution of algorithm-assigned physiological patterns.
- Comparison of algorithm classifications with laboratory global ratings.
- Sensitivity and specificity calculations for agreement with the laboratory classification.
- Cohen's kappa coefficient to assess agreement.
- Wilson 95% confidence intervals for proportions.

Agreement analyses were restricted to classifiable tests.

Statistical analyses were performed using Python.

## 6. Main findings

### 6.1 Study population and exercise characteristics

- Median age: 64 years (IQR 54–69).
- Women: 86%.
- Median peak VO₂: 15.8 mL/kg/min.
- Median peak VO₂: 88% predicted.

Only 11 of the 36 tests (31%) met both predefined exercise effort criteria.

### 6.2 Algorithm classification

The scripted algorithm identified a specific physiological abnormality in 9 of 36 tests (25%; 95% CI 14–41%).

The distribution was:

| Physiological pattern | Number of tests |
|---|---:|
| Pulmonary vascular / ventilatory inefficiency | 4 |
| Ventilatory limitation | 3 |
| Cardiovascular limitation (exercise BP fall) | 2 |
| **Total specific abnormalities** | **9** |

The remaining classifications were:

| Classification | Number | Percentage |
|---|---:|---:|
| Normal | 16 | 44% |
| Deconditioning | 8 | 22% |
| Unclassifiable | 3 | 8% |

### 6.3 Agreement with laboratory global rating

The laboratory rated 12 tests as abnormal, 11 of which had peak VO₂ <80% predicted.

Of the 9 specific abnormalities identified by the algorithm, only 4 were rated abnormal by the laboratory.

The remaining 5 tests were rated normal despite the algorithm identifying specific physiological abnormalities. All 5 had preserved peak VO₂ (80–147% predicted), including both cases of exercise-induced blood pressure fall.

Agreement analysis in 33 classifiable tests showed:

| Agreement measure | Result |
|---|---:|
| Sensitivity | 9/10 |
| Specificity | 15/23 |
| Cohen's kappa | 0.46 |

These findings highlight potential discrepancies between global laboratory interpretation and rule-based identification of specific physiological abnormalities.

## 7. Study limitations

Several limitations should be considered:

- Small sample size (n=36).
- Retrospective, single-centre design.
- Frequently limited exercise effort, with only 31% of tests meeting both effort criteria.
- Incomplete physiological measurements.
- Oxygen saturation (SpO₂) and breathing pattern were not recorded, preventing assessment of exercise-induced desaturation and dysfunctional breathing.
- The classification algorithm has not yet undergone external validation.
- The laboratory global rating is not an independent diagnostic gold standard.

Larger prospective studies are needed to validate the algorithm and assess its generalisability.

## 8. Software and reproducibility

The analytical workflow is developed using Python.

The repository includes:

- `src/classify_cpet.py`: Python implementation of the pre-specified CPET classification algorithm.
- `analysis/`: Reserved for additional statistical analyses.
- `manuscript/`: Research abstracts, manuscript drafts and supplementary materials.

The classification algorithm uses predefined rules rather than thresholds optimised retrospectively against the study dataset.

Further statistical scripts and documentation will be added as the analytical workflow develops.

## 9. Data governance and confidentiality

The GitHub repository is initially maintained as a private repository.

Patient-level clinical data, raw CPET exports and potentially identifiable information must remain in approved institutional storage.

Only research materials that have undergone appropriate institutional review and received authorisation for sharing may be included in a future public release.

## 10. Project status

| Component | Status |
|---|---|
| Study design and research objectives | Defined |
| CPET classification algorithm | Implemented |
| Synthetic classification tests | Passed |
| Descriptive analysis | Completed |
| Algorithm–laboratory agreement analysis | Completed |
| Manuscript abstract | Completed |
| Additional statistical analyses | Pending |
| External validation | Future research |
| Repository documentation | In development |
| Zenodo DOI registration | Planned |

## 11. Citation and availability

The repository DOI and public access information will be added following an approved research release through Zenodo.

Research code and supporting documentation will be shared subject to institutional data governance and publication requirements.

---

**Study design:** Single-centre retrospective observational study  
**Study population:** 36 adults with unexplained dyspnoea  
**Programming language:** Python  
**Code repository:** GitHub  
**Research archiving:** Zenodo (planned)
