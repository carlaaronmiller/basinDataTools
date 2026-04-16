import pandas as pd
from pathlib import Path
from scripts.proCVParser import parse_folder


# Points to tests/fixtures/solutions/ relative to this test file
FIXTURES = Path(__file__).parent / "fixtures"


def test_comparePD_regular():  # Compare the output of the parser to a known solution for a regular format file.
    soln = pd.read_csv(FIXTURES / "solutions/procv_solution_regular.csv")
    test_output = parse_folder(FIXTURES / "proCVSampleData/61 - January 15, 2026 (Regular)/PRO CV")
    pd.testing.assert_frame_equal(soln, test_output)


def test_comparePD_extended():  # Compare the output of the parser to a known solution for an extended format file.
    soln = pd.read_csv(FIXTURES / "solutions/procv_solution_extended.csv")
    test_output = parse_folder(FIXTURES / "proCVSampleData/60 - April 17, 2025 (Extended)/PROCV")
    pd.testing.assert_frame_equal(soln, test_output)


def test_comparePD_mixed():  # Mixed files here, so parse_folder should return None.
    test_output = parse_folder(FIXTURES / "proCVSampleData/62 - April 17, 2025 (Mixed)/PROCV")
    assert test_output is None
