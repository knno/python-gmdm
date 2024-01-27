# -*- coding: utf-8 -*-
import filecmp
import os
import re

import json5
import yaml


def get_json_field(field, string):
    match = re.search(rf'"{field}":\s*', string)
    if match:
        start = match.span()[0]
        dstr = string[start:]
        s = 0
        end = start+1
        for i, c in enumerate(dstr):
            if c == '{':
                s += 1
            elif c == '}':
                s -= 1
                if s == 0:
                    end = i+1
                    break
    data = json5.loads("{" + dstr[:end] + "}")
    return data.get(field)


def read_yaml(filepath):
    """Open and read YAML file and return a dictionary representation.
    """

    with open(filepath, "r", encoding="utf-8") as stream:
        ymldic = yaml.safe_load(stream)
        return ymldic


def compare_directories(left, right, both_directions=False):
    """Return -1 if left dir is newer than right, or 1, or 0.
    This will compare each file to find the directory with newest file.
    Using mtime and cmp.
    """
    compared = 0
    compared_left = -1000
    compared_right = -1000
    left_files = []
    right_files = []
    right_diff_files = []

    for left_file in os.listdir(left):
        left_files.append(
            (left_file, os.path.getmtime(left + os.sep + left_file)))

    for right_file in os.listdir(right):
        if right_file not in [f[0] for f in left_files]:
            right_diff_files.append(
                (right_file, os.path.getmtime(right + os.sep + right_file)))
        else:
            right_files.append(
                (right_file, os.path.getmtime(right + os.sep + right_file)))

    if len(right_diff_files) > 0:
        compared = -1

    elif len(left_files) > len(right_files):
        compared = 1

    else:
        compared_left = 0
        compared_right = 0

        for right_set in right_files:
            left_set = [f for f in left_files if f[0] == right_set[0]][0]

            left_file = left + os.sep + left_set[0]
            right_file = right + os.sep + right_set[0]

            if filecmp.cmp(left_file, right_file):
                if both_directions and compared is None:  # Previous comparison happened...
                    compared = 0
                    break
                compared = None
                break

            if left_set[1] == right_set[1]:
                continue
            else:
                compared_left = max(left_set[1], compared_left)
                compared_right = max(right_set[1], compared_right)
                compared = None

    if compared is not None:
        if compared_left > compared_right:
            compared = 1
        if compared_left < compared_right:
            compared = -1
        if compared_left == compared_right:
            compared = 0
    else:
        compared = 0

    return -1 if compared < 0 else 1 if compared > 0 else 0
