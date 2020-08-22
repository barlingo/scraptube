# Scraptube

## Description

- Queries the main host of videos of the internet and downloads the entery query result.
- It labels the data inside each video to match the query. Needs to be done manually unfortunately.

## Usage

- python run.py
  - Options:
    - -s --search: Main query to be search (Not literal)
    - -a --added-search: Added parameter to be search or excluded. e.g. +exercise -music ...
    - -d --download: Download files to ./output/{main_query} folder
    - -c --clean: Removes video duplicates in the ./output/{query} folder.
    - -l --label: Start labelling app to mark from main labels contained in labels.txt file. e.g. -l ./output/{query}
    - -n --number: Displays a histogram of all the labels contained in json files in the ./output/ folder.

