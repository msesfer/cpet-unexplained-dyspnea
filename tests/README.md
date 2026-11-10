CPET classification regression tests
These tests exercise the existing frozen implementation in src/classify_cpet.py.
They use synthetic inputs only; no patient-level data are included.
Install test dependencies
From the repository root:
python -m pip install pytest numpy pandas
Run
python -m pytest -q
The test module does not modify src/classify_cpet.py. If the frozen script is intentionally changed in a future version, review the analysis-plan implications and update the tests alongside a documented new algorithm version.
