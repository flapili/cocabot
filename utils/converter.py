# coding: utf-8
from typing import List

import dateparser as dp


def dateparse(argument: str):
    result = dp.parse(argument)
    if result is not None:
        return result

    raise ValueError(f"{argument} does not match with any format.")


def reddit_enum(argument: str):
    valid_categories: List[str] = ["hot", "new", "top", "rising"]
    if argument in valid_categories:
        return argument

    formated_valid_categories: str = "\n".join(f"{i}: {cat}" for i, cat in valid_categories)
    raise ValueError(
        f"{argument} is not valid, valid categories are\n{formated_valid_categories}"
    )
