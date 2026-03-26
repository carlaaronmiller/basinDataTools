from pathlib import Path
import re
import os
import datetime
# Version 1.2 - Added in date matching for data line vs folder date.

# Modify the filepath to point to the data.
filePath = Path(
    r"C:\Users\carla\OneDrive - Dalhousie University\desktop Save\Desktop\pythonPROCV\61 - January 15, 2026\PRO CV"
)
# Format: ...Data / surveyDate/ ProCV / Folder with Station File

# Add a folder in for the processed data in csv form.
outputDir = filePath / "processed"
outputDir.mkdir(exist_ok=True)


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
    return True


def writeLine(line):
    with open(outputFileName, mode="a", newline="") as outputFile:
        outputFile.write(line)


wasWriting = False
startLine = 0
endLine = 0
lineCounter = 0

outputFileName = outputDir / "parsedOutput.csv"
columnHeaders = "surveyFolder,fileName, Measurement type,Year,Month,Day,Hour,Minute,Second,Zero A/D,Current A/D,CO2,IRGA temperature,Humidity,Humidity sensor temperature,Cell gas pressure,Battery voltage\n"
# write the first line, using "w" option to clear the file if it already exists to prevent double appending.
try:
    with open(outputFileName, mode="w", newline="") as outputFile:
        outputFile.write(columnHeaders)
except PermissionError:
    print("The excel file is already open, please close it !")

surveyDate = filePath.parent.name

print(f"Starting PROCV parsing for the following folder:\n{filePath} \n")

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
                    writeLine(f'"{surveyDate}","{stationName}",{fileLine}')
                    pass
                else:  # If not writing,
                    if wasWriting:  # Stop writing.
                        endLine = lineCounter
                        print(f"Wrote lines {startLine} to {lineCounter}")
                        wasWriting = False
                lineCounter += 1
    print("\n")

print("Finished parsing.")
