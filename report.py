#!/usr/bin/env python3

import json
import csv
import datetime

def main():
    data = read_json_file('result.json')
    reports = generate_reports(data)
    output_file_path = write_csv_reports(reports)
    print_confirmation(output_file_path)

def read_json_file(path):
    with open(path) as json_file:
        return json.load(json_file)

def generate_reports(data):
    all_messages = data['messages']
    all_voice_messages = extract_voice_messages(all_messages)
    unique_author_ids, authors = extract_authors(all_voice_messages)

    reports = []
    for author_id in unique_author_ids:
        author = next(author for author in authors if author['id'] == author_id)
        report = generate_report(author, all_voice_messages)
        
        reports.append(report)
    
    return reports

def extract_voice_messages(messages):
    def is_voice_message(item):
        return 'media_type' in item and item['media_type'] == 'voice_message' and item['type'] == 'message'

    return [m for m in messages if is_voice_message(m)]

def extract_authors(voice_messages):
    authors = []
    unique_author_ids = set()
    for voice_message in voice_messages:
        if not voice_message['from_id'] in unique_author_ids:
            unique_author_ids.add(voice_message['from_id'])
            authors.append({
                'id': voice_message['from_id'],
                'name': voice_message['from']
            })
    return unique_author_ids, authors

def generate_report(author, all_voice_messages):
    report = {
        'name': author['name'],
        'by_day': {}
    }

    messages = extract_author_messages(author['id'], all_voice_messages)
    unique_dates = set()

    for message in messages:
        date = message['date'][0:10]
        if not date in unique_dates:
            unique_dates.add(date)
            report['by_day'][date] = 0
        
        report['by_day'][date] += message['duration_seconds']

    return report

def extract_author_messages(author_id, voice_messages):
    def is_author_id(message):
        return message['from_id'] == author_id

    return [m for m in voice_messages if is_author_id(m)]

def write_csv_reports(reports):
    csv_path = build_csv_file_name()
    with open(csv_path, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['Report'])

        for report in reports:
            writer.writerow([report['name']])

            writer.writerow(['Date', 'Interval', 'Duration (seconds)'])
            for date, duration in sorted(report['by_day'].items()):
                writer.writerow([date, get_interval_from_seconds(duration), duration])

            writer.writerow([''])
    return csv_path

def build_csv_file_name():
    current_time = datetime.datetime.utcnow().isoformat()
    return 'report.' + current_time + '.csv'

def get_interval_from_seconds(seconds):
    return datetime.timedelta(seconds=seconds)

def print_confirmation(output_file_path):
    print('Report successfully created!')
    print('Filename: ' + output_file_path)

main()