#!/usr/bin/env python3

import json
import csv
import datetime


def generate_report(json_file_path='result.json', output_dir=''):
    data = read_file(json_file_path)
    voice_messages = extract_voice_messages(data)
    graph = generate_graph_report(voice_messages)
    author_map = extract_author_map(voice_messages)
    table = transform_to_table_report(graph, author_map)
    report_filename = write_csv_report(table, output_dir)
    print('Report generated: ' + report_filename)
    return report_filename


def read_file(path):
    with open(path) as file:
        return json.load(file)


def extract_voice_messages(data):
    def is_voice_message(item):
        return 'type' in item \
               and 'duration_seconds' in item \
               and 'media_type' in item \
               and item['media_type'] == 'voice_message' \
               and item['type'] == 'message'

    return [m for m in data['messages'] if is_voice_message(m)]


def extract_author_map(voice_messages):
    author_map = {}
    unique_author_ids = set()
    for voice_message in voice_messages:
        author_id = voice_message['from_id']
        author = voice_message['from']

        if author_id in unique_author_ids:
            continue

        unique_author_ids.add(author_id)
        author_map[author_id] = author

    return author_map


def generate_graph_report(voice_messages):
    report = {}

    for message in voice_messages:
        author_id = message['from_id']
        date = message['date'][0:10]

        if author_id not in report:
            report[author_id] = {}
        if date not in report[author_id]:
            report[author_id][date] = 0

        report[author_id][date] += message['duration_seconds']

    return report


def transform_to_table_report(report, author_map):
    author_ids = list(report.keys())
    all_dates = set()

    for author_id in author_ids:
        author_dates = list(report[author_id].keys())
        [all_dates.add(author_date) for author_date in author_dates]

    rows = []
    headers = ['Date']
    [headers.append(author_map[author_id]) for author_id in author_ids]

    for date in sorted(all_dates):
        cells = [date]
        for author_id in author_ids:
            duration = None
            if date in report[author_id]:
                duration = get_interval_from_seconds(report[author_id][date])
            cells.append(duration)
        rows.append(cells)
    return {'headers': headers, 'rows': rows}


def write_csv_report(table, output_dir):
    csv_filename = build_csv_file_name()
    csv_path = output_dir + csv_filename
    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(table['headers'])
        [writer.writerow(row) for row in table['rows']]

    return csv_filename


def build_csv_file_name():
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime('%Y%m%d%H%M%S')
    return 'report.' + timestamp + '.csv'


def get_interval_from_seconds(seconds):
    return datetime.timedelta(seconds=seconds)


if __name__ == '__main__':
    generate_report()
