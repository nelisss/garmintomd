# Garmin to markdown

### Introduction

This script allows you to convert a CSV file with Garmin activities to markdown files, one for each activity. These markdown files can subsequently be imported into a note taking app, for instance.

### Requirements

- Python 3.8 or higher

### Installation

1. Clone this repository into a directory of your choice

```
cd /path/to/directory
git clone https://github.com/nelisss/garmintomd
```

1. Run install.sh to create a virtual environment with the required python packages installed

```
chmod +x install.sh
./install.sh
```

### Usage

**Download Garmin activities CSV**

- Garmin Connect CSV: from https://connect.garmin.com/modern/activities, scroll down as far as you want and press Export CSV.
  - Only the activities that are loaded on the web page will be exported into the CSV file. This can cause problems when you want to export a lot of activities. However, I don't know of any other way to batch export activities into a CSV file.

**Run the python script**

1. Activate the virtual environment

```
source venv/bin/activate
```

1. Run the python script

```
python garmintomd.py [options]
```

The following options are recognized:

| Option            | Description                                                                          | Possible values                                                          |
|-------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| \-h --help         | Print help.                                                                          | \-                                                                        |
| \-f --file         | Path to Garmin CSV file. Default: interactive file picker.                           | Valid path to CSV file or "interactive" to be prompted with file picker. |
| \-d --directory    | Output directory to save .md files to. Default: \<working directory\>/output.          | Valid path to folder. Can create one folder, but not recursively.        |
| \-o --frontmatter  | Type of frontmatter to add to .md files. Default: "none".                            | Currently only supports "joplin" or "none".                              |
| \-z --timezone     | Timezone to use for datetime extracted from CSV. Default: system timezone.           | Timezone in IANA format (TZ identifier in [this](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) table).                   |
| \-t --favorite-tag | Whether to add a tag "Favorite" to the frontmatter of activities with favorite=true. Default: true. | true/t or false/f                                                        |

### Combine with Strength Level

The markdown files resulting from this script can be combined with the output of another script, [strengthleveltomd](https://github.com/nelisss/strengthleveltomd), by using [garminslcombinemd](https://github.com/nelisss/garminslcombinemd).
