"""Spylt helpers. Mostly just functions to convert objects to JS equivalents"""
from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any, Union

from json import JSONEncoder
import re

from .exceptions import PointerNotFoundError


def flatten_dict(dic: dict[str, Any]) -> dict[str, Any]:
    items: list[Any] = []
    for key, value in dic.items():
        if isinstance(value, MutableMapping):
            items.extend(flatten_dict(value).items())  # type: ignore
        else:
            items.append((key, value))
    return dict(items)


def js_list(encoder: JSONEncoder, data: list) -> str:
    pairs = []
    for value in data:
        pairs.append(js_val(encoder, value))
    return "[" + ", ".join(pairs) + "]"


def js_dict(encoder: JSONEncoder, data: dict) -> str:
    pairs = []
    for k, v in data.items():
        pairs.append(k + ": " + js_val(encoder, v))
    return "{" + ", ".join(pairs) + "}"


def js_val(encoder: JSONEncoder, data: Union[dict, list, Any]) -> str:
    if isinstance(data, dict):
        val = js_dict(encoder, data)
    elif isinstance(data, list):
        val = js_list(encoder, data)
    else:
        val = encoder.encode(data)
    return val


def replace_some(text: str, conversion_dict: dict[str, Any]) -> str:
    for key, value in conversion_dict.items():
        text = text.replace(key, value)
    return text


def find_pointer(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
        if not "point" in lines[0]:
            raise PointerNotFoundError(
                "No Python file is being pointed to. "
                "Please add a comment at the top of your Svelte code "
                "(ex: <!-- point App.py:app -->)"
            )
        pointer = (
            lines[0]
            .replace("point", "")
            .replace("<!--", "")
            .replace("-->", "")
            .replace(" ", "")
            .strip()
        )
        return pointer


UNDERSCORE_RE = re.compile(r"(?<=[^\-_])[\-_]+[^\-_]")


def camelize(string: str) -> str:
    if " " in string:
        s = "_".join(map(lambda s: s.lower(), string.split(" ")))
    else:
        s = re.sub(r"\s+", "", str(string))

    if len(s) != 0 and not s[:2].isupper():
        s = s[0].lower() + s[1:]

    return UNDERSCORE_RE.sub(lambda m: m.group(0)[-1].upper(), s)
