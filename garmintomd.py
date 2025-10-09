import tkinter as tk
from tkinter import filedialog
import getopt
import sys
import os
import pytz
from tzlocal import get_localzone_name
import pandas as pd
from tqdm import tqdm

### Get command-line arguments
args = sys.argv[1:]
options = "hf:d:o:z:t:"
long_options = ["help", "file=", "directory=", "frontmatter=", "timezone=", "favorite-tag="]

garmin_csv_path = "interactive"
output_dir = os.getcwd()
frontmatter = "none"
timezone = get_localzone_name()
favorite_tag = True

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for arg, val in arguments:
        if arg in ("-h", "--help"):
            print("Help")
            sys.exit()

        if arg in ("-f", "--file"):
            garmin_csv_path = val
            if not os.path.exists(garmin_csv_path):
                raise FileExistsError("\nProvided garmin CSV file path does not exist.")

        if arg in ("-d", "--directory"):
            output_dir = val
            if not os.path.exists(output_dir):
                try:
                    os.mkdir(output_dir)
                except Exception as e:
                    raise FileExistsError("\nProvided output directory does not exist and could not be created.") from e
            
        if arg in ("-o", "--frontmatter"):
            frontmatter = val
            if frontmatter not in ["none", "joplin"]:
                raise ValueError("\nProvided frontmatter is not supported. Possible values: none, joplin.")

        if arg in ("-z", "--timezone"):
            timezone = val
            try:
                pytz.timezone(timezone)
            except Exception as e:
                raise ValueError("\nInvalid value for argument timezone. Should be in IANA format, for example Europe/Amsterdam.") from e 

        if arg in ("-t", "--favorite-tag"):
            favorite_tag = val
            if favorite_tag.lower() == "t" or favorite_tag.lower() == "true":
                favorite_tag = True
            elif favorite_tag.lower() == "f" or favorite_tag.lower() == "false":
                favorite_tag = False
            else:
                raise ValueError("\nInvalid value for argument favorite-tag. Should be true/t or false/f.")

except getopt.error as err:
    print(str(err))

print(" ")
print(f"Running garmintomd with the following parameters:\n   Input file: {garmin_csv_path}\n   Output directory: {output_dir}\n   Frontmatter: {frontmatter}\n   Add tags for favorites (Joplin): {favorite_tag}\n")

### Import garmin CSV
if garmin_csv_path == "interactive":
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    garmin_csv_path = filedialog.askopenfilename(
        title="Select Garmin activities CSV", initialdir=os.getcwd()
    )
    print("Selected file:")
    print(garmin_csv_path, "\n")

cols = ["Activity Type", "Date", "Favorite", "Title", "Distance", "Calories", "Time", "Avg HR", "Max HR", "Avg Pace", "Best Pace", "Total Ascent"]
dtypes = {"Activity Type": "str", "Favorite": "str", "Title": "str", "Distance": "float", "Calories": "float", "Time": "str", "Avg HR": "float", "Max HR": "float", "Avg Pace": "str", "Best Pace": "str", "Total Ascent": "float"}
activities = pd.read_csv(garmin_csv_path, na_values="--", decimal=",", thousands=".", 
    usecols=cols,
    dtype=dtypes)

### Preprocessing of DataFrame
activities["Date"] = pd.to_datetime(activities["Date"])
activities["Date"] = activities["Date"].dt.tz_localize(timezone).dt.tz_convert("UTC")

### Convert each row to markdown file
file_names = []
with tqdm(total=len(activities.index), desc="Converting to markdown") as pbar:
    for row_ind, row in activities.iterrows():
        # Add frontmatter if frontmatter destination was given
        if frontmatter == "joplin":
            frontmatter_string = \
f"""---
title: \"{row["Title"]}\"
created: {str(row["Date"].isoformat()).replace("T", " ").replace("+00:00", "") + "Z"}{("\ntags:\n  - Favorite") if favorite_tag & (row["Favorite"] == "true") else ""}
---

"""
        else:
            frontmatter_string = ""

        # Add content common to all activity types
        content_string = \
f"""{f"**{row["Title"]}**\n" if frontmatter == "none" else ""}Activity type: {row["Activity Type"]}
Date: {row["Date"].strftime("%A %B %-d %Y")}
Duration: {row["Time"].split(":")[0] if row["Time"].split(":")[0] != "0" else ""}{(" hour and " if row["Time"].split(":")[0] == "1" else " hours and ") if row["Time"].split(":")[0] != "0" else ""}{int(row["Time"].split(":")[1])} {"minutes" if int(row["Time"].split(":")[1]) != 1 else "minute"}
"""

        # Add specific content for specific activity types
        if row["Activity Type"] in ["Running", "Treadmill Running", "Hiking", "Walking"]:
            content_string = content_string + \
f"""Distance: {row["Distance"]:.2f} km
Pace: {row["Avg Pace"]} min/km (*average*), {row["Best Pace"]} min/km (*max*)
Ascent: {row["Total Ascent"]:.0f} m
"""
        elif row["Activity Type"] in ["Cycling", "Mountain Biking"]:
            content_string = content_string + \
f"""Distance: {row["Distance"]:.2f} km
Speed: {row["Avg Pace"].replace(",", ".")} km/h (*average*), {row["Best Pace"].replace(",", ".")} km/h (*max*)
Ascent: {row["Total Ascent"]:.0f} m
"""
        elif row["Activity Type"] in ["Open Water Swimming", "Pool Swim"]:
            content_string = content_string + \
f"""Distance: {row["Distance"]:.2f} m
Speed: {row["Avg Pace"]} min/100m (*average*), {row["Best Pace"] if not pd.isna(row["Best Pace"]) else "-"} min/100m (*max*)
"""
        else:
            pass

        content_string = content_string + \
f"""Calories: {row["Calories"]:.0f}{f"\nHeart rate: {row["Avg HR"]:.0f} bpm (*average*), {row["Max HR"]:.0f} bpm (*max*)" if not pd.isna(row["Avg HR"]) and not pd.isna(row["Max HR"]) else ""}
"""

        file_name = f"{row["Date"].strftime("%Y-%m-%d")}_{row["Activity Type"]}".replace(" ", "_")

        file_name_ind = 1 
        file_name_base = file_name
        while file_name in file_names:
            file_name = file_name_base + "_" + str(file_name_ind)
            file_name_ind = file_name_ind + 1

        with open(f"{output_dir}{"/" if output_dir[-1] != "/" else ""}{file_name}.md", "w", encoding="utf-8") as md_file:
            md_file.write(frontmatter_string + content_string)

        file_names.append(file_name)
        pbar.update(1)
