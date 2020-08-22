import json
from collections import Counter
import pathlib


def get_labels(file):

    with open(file) as file:
        file_content = file.readlines()
    labels = [x.strip() for x in file_content]
    return labels


def __case_insensitive_str(string):
    str_case_ins = ""
    for char in string:
        if char.isalpha():
            lower = char.lower()
            upper = char.upper()
            char_case_ins = f'[{lower}{upper}]'
            str_case_ins += char_case_ins

    return str_case_ins


def list_types_in_path(path, filetype):

    str_search = "**/*."
    str_search += __case_insensitive_str(filetype)
    path_list = list(pathlib.Path(path).rglob(str_search))
    return path_list


def count_json_entries(filepath, entry):
    with open(filepath, 'r') as json_file:
        item_dict = json.load(json_file)
        map_entry_len = Counter(item_dict[entry])

    return map_entry_len


def count_all_labels(main_path, query):
    json_files = list_types_in_path(main_path, "json")
    sum_entries = {}
    for file in json_files:
        json_entries = count_json_entries(file, query)
        for entry in json_entries:
            num_entries = json_entries[entry]
            try:
                sum_entries[entry] += num_entries
            except:
                sum_entries[entry] = num_entries

    return sum_entries
