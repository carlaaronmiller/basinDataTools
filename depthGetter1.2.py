import os
import re
import csv
import sys
import msvcrt
# Get the folder the script is dropped into
folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# Use raw string to avoid backslash issues

#folder_path = r"C:\Users\carla\OneDrive - Dalhousie University\CERC Ocean\Projects\Bedford Basin Planetary\Data\91- March 10, 2026 (Bi-weekly)\Rosette"
folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))

depth_results = {}

# Regex to find bottle header lines
bottle_line_pattern = re.compile(
    r"^\s*(\d+)\s+(\w+ \d+ \d{4})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)"
)

for filename in os.listdir(folder_path):
    if filename.endswith(".btl"):
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8", errors="replace") as file:
            print(filename)
            for line in file:
                match = bottle_line_pattern.match(line)
                if match:
                    bottle_num = int(match.group(1))
                    date = match.group(2)
                    depth = float(match.group(5))  # DepSM column
                    key = f"{filename}_bottle_{bottle_num}"
                    depth_results[key] = {
                        "date": date,
                        "depth_m": depth,
                        "file": filename,
                        "bottle": bottle_num,
                    }

# Display results
for bottle, data in sorted(depth_results.items()):
    print(
        f"Bottle {bottle}: {data['depth_m']} m on {data['date']} (from {data['file']})"
    )


# Define CSV output path
output_csv = os.path.join(folder_path, "bottleDepthSummary.csv")

# Write results to CSV
with open(output_csv, "w", newline="") as csvfile:
    fieldnames = ["date", "filename", "bottle", "depth_m"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data in depth_results.values():
        writer.writerow(
            {
                "date": data["date"],
                "filename": data["file"],
                "bottle": data["bottle"],
                "depth_m": data["depth_m"],
            }
        )

print(f"\n✅ Results saved to: {output_csv}")
print("Press any key to continue...")
msvcrt.getch()
