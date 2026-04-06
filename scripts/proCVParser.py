from pathlib import Path
import re
import os
import datetime
import pandas as pd
from io import StringIO
# Version 1.2 - Added in date matching for data line vs folder date.

columnHeaders = "surveyFolder,fileName, Measurement type,Year,Month,Day,Hour,Minute,Second,Zero A/D,Current A/D,CO2,IRGA temperature,Humidity,Humidity sensor temperature,Cell gas pressure,Battery voltage\n"


# Check if the data line if validly formatted, and that the dates match between the data and the folder.
def isValidLine(fileLine, folderDate):
    fileLinePattern = r"^(\w\s\w)(,[^,\s]{0,7}){14}"
    fileLineMatch = re.search(fileLinePattern, fileLine)
    if fileLineMatch is None:
        return False
    # 1 - Get the date from the data line.
    lineDate = datetime.datetime(
        int(fileLineMatch[0][4:8]),
        int(fileLineMatch[0][9:11]),
        int(fileLineMatch[0][12:14]),
    )
    # 2 - Get date from the folder path.
    folderDatePattern = r"(\w+ \d+, \d+)"
    folderDateMatch = re.search(folderDatePattern, folderDate)
    if folderDateMatch is None:
        return False
    format_pattern = "%B %d, %Y"
    folderDate = datetime.datetime.strptime(folderDateMatch[0], format_pattern)
    if folderDate != lineDate:
        print(
            f"Mismatch between folder date: {folderDate}, and data point date: {lineDate}"
        )
        return False
    return True


# Parses data from all files in folder into a pandas data frame.
# Only adds line which have date matching the parent folder date.
def parseFolder(filePath):
    rows = []
    surveyDate = filePath.parent.name
    wasWriting = False
    startLine = 0
    lineCounter = 0

    for item in filePath.iterdir():
        if item.is_dir():
            continue
        else:
            lineCounter = 0
            stationName = item.name
            print(stationName)
            # Step 1: Open the file.
            with open(item, "r") as inputFile:
                for fileLine in inputFile:
                    if isValidLine(fileLine, surveyDate):  # If valid
                        if not wasWriting:  # If starting, start and counter.
                            startLine = lineCounter
                            wasWriting = True
                        # Otherwise, just write the line as normal.
                        rows.append(f'"{surveyDate}","{stationName}",{fileLine}')
                        pass
                    else:  # If not writing,
                        if wasWriting:  # Stop writing.
                            print(f"Parsed lines {startLine} to {lineCounter}")
                            wasWriting = False
                    lineCounter += 1
        print("\n")

    data = columnHeaders + "".join(rows)
    return pd.read_csv(StringIO(data))


# Write the parsed in csv format to output directory.
def writeSummary(df, outputDir):
    outputDir.mkdir(exist_ok=True)
    outputFileName = outputDir / "parsedOutput.csv"
    try:
        df.to_csv(outputFileName, index=False)
    except PermissionError:
        print("The excel file is already open, please close it!")


if __name__ == "__main__":
    # Format: ...Data / surveyDate/ ProCV / Station1.txt, station2.txt etc.
    filePath = Path(
        r"C:\Users\carla\OneDrive - Dalhousie University\desktop Save\Desktop\New folder (3)\basinDataTools\tests\fixtures\proCVSampleData\61 - January 15, 2026\PRO CV"
    )
    print(f"Starting PROCV parsing for the following folder:\n{filePath} \n")
    df = parseFolder(filePath)
    writeSummary(df, filePath / "processed")
    print("Finished parsing.")
