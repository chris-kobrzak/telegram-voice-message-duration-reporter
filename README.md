# telegram-voice-message-duration-reporter

Reads [Telegram](https://telegram.org) conversations [exported to
JSON](https://telegram.org/blog/export-and-more) and builds a CSV file with a report on
total duration of voice messages on a per user per day basis.

## Why?

This is a real-world project. The requirement is to be able to produce visual graph
reports of students' engagement measured by the length of voice messages they exchange
with their tutors over the Telegram app.

## Prerequisites
- Python 3
- Telegram Desktop

## Usage

1. Export conversations in the JSON format with Telegram Desktop
2. Put the exported `result.json` file and the `report.py` script in the same directory
3. On Windows simply double click `report.py`. On Unix systems open a terminal and run

    ```bash
    ./report.py
    ```
4.  This will generate a CSV file in the same directory with the following name pattern:
`report.<timestamp>.csv`.

### Sample report

<img src="./sample-report.png" width="350" alt="Sample report screengrab" />
