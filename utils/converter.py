# coding: utf-8
from typing import List

import dateparser as dp


def dateparse(argument: str):
    result = dp.parse(argument)
    if result is not None:
        return result

    raise ValueError(f"{argument} does not match with any format.")


def str_enum(choices: List[str]):
    def converter(argument: str):
        if argument in choices:
            return argument

        raise ValueError(
            f" {argument} is not valid, valid choice are : {', '.join(f'`{c}`' for c in choices)}"
        )

    return converter
