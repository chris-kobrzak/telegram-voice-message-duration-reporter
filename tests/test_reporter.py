import datetime

import pytest
from reporter import build_csv_file_name

@pytest.fixture
def sample_datetime():
    return datetime.datetime(2023, 1, 1, 12, 25, 30)

def test_default_build_csv_file_name(sample_datetime):
    expected_output = "report.20230101122530.csv"
    result = build_csv_file_name(sample_datetime)
    assert result == expected_output
