# -*- coding: utf-8 -*-
def dotget(dictionary, dot_str):
    """Access a nested dot notation in dict."""
    dots = dot_str.split(".")
    while len(dots) > 0:
        dictionary = dictionary.get(dots.pop(0), {})
    return dictionary


def dotset(dictionary, dot_str, value):
    """Set a value by dot notation on dict."""
    dots = dot_str.split(".")
    for key in dots[:-1]:
        dictionary = dictionary.setdefault(key, {})
    dictionary[dots[-1]] = value
