#!/usr/bin/env python3

import datetime
import pandas as pd
import time_utils as tu

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
        (messages['from_id'].str.startswith('user')) &
        (messages['duration_seconds'].notna())
    ]
    df = df[['date', 'date_unixtime', 'duration_seconds', 'from_id', 'from']]
    df = df.rename(columns={
        'from_id': 'User ID',
        'from': 'Name',
        'date': 'Date',
        'date_unixtime': 'Epoch Time',
        'duration_seconds': 'Duration (s)'
    })

    return df


def produce_report_with_stats(voice_messages):
    df = voice_messages
    df['User ID'] = df['User ID'].str.removeprefix('user').astype(int)
    df['Date'] = df['Date'].str[0:10]

    df = df.groupby(['User ID', 'Name', 'Date']).agg(
        First_Msg=('Epoch Time', 'min'),
        Last_Msg=('Epoch Time', 'max'),
        Duration=('Duration (s)', 'sum'))
    df['First_Msg'] = df['First_Msg'].astype(int)
    df['Last_Msg'] = df['Last_Msg'].astype(int)

    df = df.pivot_table(
        index='Date',
        columns=['Name', 'User ID'],
        values=['Duration', 'First_Msg', 'Last_Msg'],
        fill_value=0)

    df['First_Msg'] = df['First_Msg'].apply(tu.epoch_time_to_time)
    df['Last_Msg'] = df['Last_Msg'].apply(tu.epoch_time_to_time)

    df.loc['Total'] = df.sum(numeric_only=True)
    df.loc['Average'] = df[:-1].mean(numeric_only=True)

    df.loc[:, "Daily total"] = df['Duration'].sum(axis=1)

    df = df.apply(tu.seconds_to_intervals)

    df = df[['Duration', 'Daily total', 'First_Msg', 'Last_Msg']]

    return df


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
