# Scraptube

## Description

- Queries the main host of videos of the internet and downloads the entery query result.
- It labels the data inside each video to match the query. Needs to be done manually unfortunately.

## Usage

- python run.py
  - Options:
  -s --search: Main query to be search (Not literal)
  -a --added-search: Added parameter to be search or excluded. e.g. +exercise -music ...
  -d --download: Download files to ./output/{main_query} folder
  -c --clean: Starts labelling the videos.

