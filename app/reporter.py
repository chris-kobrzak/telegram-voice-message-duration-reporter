#!/usr/bin/env python3

import csv
import datetime
import pandas as pd


def generate_report(json_file_path='result.json', output_dir=''):
    messages = extract_messages(json_file_path)
    voice_messages = find_voice_messages(messages)
    report = produce_report_with_stats(voice_messages)
    report_filename = write_csv_report(report, output_dir)
    print('Report generated: ' + report_filename)
    return report_filename


def extract_messages(json_file_path):
    df = pd.read_json(json_file_path)
    return df.messages.apply(pd.Series)


def find_voice_messages(messages):
    pd.options.mode.chained_assignment = None
    df = messages[
        (messages['type'] == 'message') &
        (messages['media_type'] == 'voice_message') &
        (messages['duration_seconds'].notna())
    ]
    df = df[['date', 'date_unixtime', 'duration_seconds', 'from_id', 'from']]
    df = df.rename(columns={
        'from_id': 'User ID',
        'from': 'Name',
        'date': 'Date',
        'date_unixtime': 'Time',
        'duration_seconds': 'Duration (s)'
    })

    return df


def produce_report_with_stats(voice_messages):
    df = voice_messages
    df['User ID'] = df['User ID'].str.removeprefix('user').astype(int)
    df['Date'] = df['Date'].str[0:10]

    df = pd.pivot_table(
        df,
        index='Date',
        columns=['Name', 'User ID'],
        aggfunc={'Duration (s)': ['sum'], 'Time': ['min', 'max']}
    )

    df.loc['Total'] = df.sum(numeric_only=True)
    df.loc['Average'] = df[:-1].mean(numeric_only=True)

    df.loc[:, "Daily total"] = df['Duration (s)'].sum(axis=1)

    df['Time'] = df['Time'].apply(unix_time_to_date)
    df = df.apply(seconds_to_intervals)

    return df


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


def unix_time_to_date(unix_time_series):
    return [
        # TODO: Format as time string
        pd.to_datetime(unix_time, unit='s').strftime('%X')
        if pd.notna(unix_time)
        else ""
        for unix_time in unix_time_series
    ]


def interval_to_string(delta, format):
    time_part = {'days': delta.days}
    time_part['hours'], rem = divmod(delta.seconds, 3600)
    time_part['minutes'], time_part['seconds'] = divmod(rem, 60)
    return format.format(**time_part)


def write_csv_report(df, output_dir):
    csv_filename = build_csv_file_name()
    csv_path = output_dir + csv_filename

    df.to_csv(csv_path)

    return csv_filename


def build_csv_file_name():
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime('%Y%m%d%H%M%S')
    return 'report.' + timestamp + '.csv'


if __name__ == '__main__':
    generate_report()
