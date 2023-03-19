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
        'date_unixtime': 'Timestamp',
        'duration_seconds': 'Duration (s)'
    })
    df['User ID'] = df['User ID'].str.removeprefix('user').astype(int)
    df['Date'] = df['Date'].str[0:10]
    return df


def produce_report_with_stats(voice_messages):
    grouped = voice_messages\
        .groupby(['User ID', 'Name', 'Date'])\
        .agg({'Duration (s)': ['sum'], 'Datetime': ['min']})
    df = grouped.pivot_table(
        values='Duration (s)',
        index='Date',
        columns=['Name', 'User ID'],
        fill_value=0
    )
    df.loc[:, "Daily total"] = df.sum(axis=1)
    df.loc['Total'] = df.sum()
    df.loc['Average'] = df[:-1].mean()
    return df.apply(seconds_to_intervals)


def seconds_to_intervals(second_series):
    return [
        interval_to_string(
            pd.Timedelta(seconds=seconds),
            "{hours}:{minutes:02d}:{seconds:02d}",
        )
        if pd.notna(seconds) and seconds > 0
        else ""
        for seconds in second_series
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
