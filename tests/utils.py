"""Module for test utils"""

import json


def get_fake_json_data(filename):
    """Gets fake data from json-file"""
    with open(f"tests/mock_files/{filename}.json", encoding="utf-8") as file:
        data = json.load(file)
    return data
