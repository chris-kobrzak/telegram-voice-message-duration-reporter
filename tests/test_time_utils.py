import pandas as pd
import pytest

from app import time_utils as tu


@pytest.fixture
def sample_unix_timestamps():
    return [1627353600, 1697439400, 1739914853]

def test_epoch_time_to_time(sample_unix_timestamps):
    expected_output = ['02:40', '06:56', '21:40']
    result = tu.epoch_time_to_time(sample_unix_timestamps)
    assert result == expected_output

def test_epoch_time_to_time_with_invalid_data():
    invalid_unix_timestamps = [1627353600, None, 1739914853]
    expected_output = ['02:40', '', '21:40']
    result = tu.epoch_time_to_time(invalid_unix_timestamps)
    assert result == expected_output


@pytest.mark.parametrize("delta, expected", [
    (pd.Timedelta(hours=1), "1:00:00"),
    (pd.Timedelta(minutes=30), "0:30:00"),
    (pd.Timedelta(seconds=45), "0:00:45"),
    (pd.Timedelta(hours=2, minutes=30, seconds=45), "2:30:45"),
])
def test_interval_to_string(delta, expected):
    assert tu.interval_to_string(delta, "{hours}:{minutes:02d}:{seconds:02d}") == expected


@pytest.mark.parametrize("second_series, expected", [
    ([3600], ["1:00:00"]),
    ([1800], ["0:30:00"]),
    ([600, 143], ["0:10:00", "0:02:23"]),
])
def test_seconds_to_intervals(second_series, expected):
    assert tu.seconds_to_intervals(second_series) == expected
