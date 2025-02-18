#!/usr/bin/env python3

import pandas as pd

def epoch_time_to_time(unix_time_series):
    return [
        pd.to_datetime(unix_time, unit='s').strftime('%H:%M')
        if pd.notna(unix_time)
        else ""
        for unix_time in unix_time_series
    ]


def seconds_to_intervals(second_series):
    return [
        interval_to_string(
            pd.Timedelta(seconds=value),
            "{hours}:{minutes:02d}:{seconds:02d}",
        )
        if pd.notna(value) and isinstance(value, (int, float)) and value > 0
        else value
        for value in second_series
    ]


def interval_to_string(delta, time_format):
    time_part = {'days': delta.days}
    time_part['hours'], rem = divmod(delta.seconds, 3600)
    time_part['minutes'], time_part['seconds'] = divmod(rem, 60)
    return time_format.format(**time_part)
