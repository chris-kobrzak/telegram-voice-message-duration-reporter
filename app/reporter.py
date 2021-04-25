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

    dates_total = len(all_dates)

    if dates_total == 0:
        return {'headers': ['Date'], 'rows': ['N/A']}

    rows = []
    headers = ['Date']
    [headers.append(author_map[author_id]) for author_id in author_ids]
    headers.append('Total per day')

    author_duration = {}
    duration_grand_total = datetime.timedelta()
    for date in sorted(all_dates):
        cells = [date]
        durations_total = datetime.timedelta()
        for author_id in author_ids:
            if author_id not in author_duration:
                author_duration[author_id] = datetime.timedelta()
            duration = None
            if date in report[author_id]:
                duration = get_interval_from_seconds(report[author_id][date])
                durations_total += duration
                author_duration[author_id] += duration
                duration_grand_total += duration
            cells.append(duration)
        cells.append(durations_total)
        rows.append(cells)

    summary_cells = ['Total cycle']
    [summary_cells.append(author_duration[author_id])
     for author_id in author_ids]
    summary_cells.append(duration_grand_total)
    rows.append(summary_cells)

    averages = ['Avg per day']
    [averages.append(format_average_duration(author_duration[author_id] / dates_total))
     for author_id in author_ids]
    averages.append(format_average_duration(
        duration_grand_total / dates_total))
    rows.append(averages)

    return {'headers': headers, 'rows': rows}


def format_average_duration(delta):
    return str(delta).split(".")[0]


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
