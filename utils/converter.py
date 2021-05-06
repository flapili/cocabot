# coding: utf-8
import dateparser


def dateparse(argument: str):
    result = dateparser.parse(argument)
    if result is not None:
        return result

    raise ValueError(f"{argument} does not match with any format.")
