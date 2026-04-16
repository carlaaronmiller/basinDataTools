import datetime
import re
from io import StringIO
from pathlib import Path

import pandas as pd

# Column Header Info:
COLUMN_HEADERS_REGULAR = (
    "surveyFolder,fileName, Measurement type,Year,Month,Day,Hour,Minute,Second,"
    "Zero A/D [counts],Current A/D [counts],CO2 [ppmv],Average IRGA temperature [ºC],"
    "Humidity [mbar],Humidity sensor temperature [ºC], Gas Pressure[mbar],Supply Volts[V]\n"
)
REGULAR_COLUMN_COUNT = 15

COLUMN_HEADERS_EXTENDED = (
    "surveyFolder,fileName, Measurement type,Year,Month,Day,Hour,Minute,Second,"
    "Zero A/D [counts],Current A/D [counts],CO2 [ppmv],Average IRGA temperature [ºC],"
    "Humidity [mbar],Humidity sensor temperature [ºC], Gas Pressure[mbar],"
    " IGRA Detector Temp[ºC], IGRA Source Temp[ºC],Supply Volts[V]\n"
)
EXTENDED_COLUMN_COUNT = 17

FILE_LINE_PATTERN = r"^(\w\s\w)(,[^,\s]{0,7}){14,16}"


def detect_output_format(file_line):
    file_line_match = re.search(FILE_LINE_PATTERN, file_line)
    if file_line_match is None:
        return [None, None]

    hits = len(file_line_match[0].split(","))
    if hits == EXTENDED_COLUMN_COUNT:
        return ["Extended", COLUMN_HEADERS_EXTENDED]
    elif hits == REGULAR_COLUMN_COUNT:
        return ["Regular", COLUMN_HEADERS_REGULAR]
    else:
        print(f"WARNING: Detected an unexpected number ({hits}) of columns in the data line, skipping line.")
        return ["Bad format", None]


# Check if the data line is validly formatted, and that the dates match between the data and the folder.
def is_valid_line(file_line, folder_date):
    file_line_match = re.search(FILE_LINE_PATTERN, file_line)
    if file_line_match is None:
        return False

    # 1 - Get the date from the data line.
    line_date = datetime.datetime(
        int(file_line_match[0][4:8]),
        int(file_line_match[0][9:11]),
        int(file_line_match[0][12:14]),
    )

    # 2 - Get date from the folder path.
    folder_date_pattern = r"(\w+ \d+,?\s\d+)"
    folder_date_match = re.search(folder_date_pattern, folder_date)
    if folder_date_match is None:
        print("No folder date found, please format it as: Survey# - Month DD, YYYY (SurveyType)")
        return False

    format_pattern = "%B %d %Y"
    # Pick up cases where comma has been missed.
    if "," in folder_date_match[0]:
        format_pattern = "%B %d, %Y"

    folder_date = datetime.datetime.strptime(folder_date_match[0], format_pattern)

    # Compare both dates.
    if folder_date != line_date:
        print(f"Mismatch between folder date: {folder_date}, and data point date: {line_date}")
        return False

    return True


# Parses data from all files in folder into a pandas data frame.
# Only adds lines which have date matching the parent folder date.
def parse_folder(file_path):
    formats_used = []
    rows = []
    data_format = None
    output_header = None  # Set once from the first valid file; survives the per-file reset.
    survey_date = file_path.parent.name
    was_reading = False
    start_line = 0
    line_counter = 0
    output_header = None

    # Get the files in alphabetical order for consistency.
    sorted_files = sorted(file_path.iterdir(), key=lambda x: x.name)

    for item in sorted_files:
        print(f"Parsing file: {item.name}")
        data_format = None

        if item.is_dir() or item.suffix not in (".log", ".txt", ""):
            print(f"Skipping {item.name}, not a .log or .txt file.\n")
            continue

        line_counter = 0
        station_name = item.name

        with open(item, "r") as input_file:
            for file_line in input_file:
                if is_valid_line(file_line, survey_date):
                    if data_format is None:  # Detect format on the first valid line.
                        detected_format = detect_output_format(file_line)
                        if detected_format[0] == "Bad format" or detected_format[0] is None:
                            print(f"WARNING: Detected an invalid data line in file {station_name}, skipping line.")
                            continue
                        format_name, data_format = detected_format
                        formats_used.append([item.name, format_name])  # Keep track of formats used in outputs.
                        if output_header is None:
                            output_header = data_format

                    if not was_reading:  # If starting to read, note the line number.
                        start_line = line_counter
                        was_reading = True

                    rows.append(f'"{survey_date}","{station_name}",{file_line}')

                else:  # If the line is invalid:
                    if was_reading:  # and you were reading, stop and print the lines you just read.
                        was_reading = False

                line_counter += 1

            if line_counter == 0:
                print(f"WARNING: No lines read from file {station_name}, check the file for formatting issues.")
            elif data_format is not None:
                print(
                    f"Filename: {station_name:<20} - lines {start_line:<5} to {line_counter:>5}, format: {format_name:<5}"
                )

        print("\n")
    format_types = {fmt[1] for fmt in formats_used}
    if "Regular" in format_types and "Extended" in format_types:
        print("ERROR: Mixed Regular and Extended formats detected — cannot combine into one table.")
        for fmt in formats_used:
            print(f"{fmt}\n")
        print("Remove or fix the mismatched files and re-run.")
        return None

    if output_header is not None:
        data = output_header + "".join(rows)
        return pd.read_csv(StringIO(data))


# Write the parsed data in csv format to the output directory.
def write_summary(df, output_dir):
    output_dir.mkdir(exist_ok=True)
    output_file_name = output_dir / "parsedOutput.csv"
    try:
        df.to_csv(output_file_name, index=False)
    except PermissionError:
        print("The excel file is already open, please close it!")


if __name__ == "__main__":
    # Format: ...Data / surveyDate/ ProCV / Station1.txt, station2.txt etc.
    file_path = Path(
        r"C:\Users\carla\OneDrive - Dalhousie University\desktop Save\Desktop\dataToolsFolder\basinDataTools\tests\fixtures\proCVSampleData\61 - January 15, 2026 (Regular)\PRO CV"
    )
    print(f"Starting PROCV parsing for the following folder:\n{file_path} \n")
    try:
        df = parse_folder(file_path)
    except FileNotFoundError:
        print("COULDN'T FIND THAT FOLDER, any TYPOS?")
        df = None

    if df is not None:
        write_summary(df, file_path / "processed")
    print("Finished program.")
