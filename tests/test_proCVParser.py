import pandas as pd
from pathlib import Path
from scripts.proCVParser import parseFolder


# Points to tests/fixtures/solutions/ relative to this test file
FIXTURES = Path(__file__).parent / "fixtures"


def test_comparePD():
    # Convert the solution into a pandas for comparison.
    soln = pd.read_csv(FIXTURES / "solutions/procv_solution.csv")
    testOutput = parseFolder(FIXTURES / "proCVSampleData/61 - January 15, 2026/PRO CV")
    pd.testing.assert_frame_equal(soln, testOutput)
