# coding: utf-8
import dateparser as dp


def dateparse(argument):
    result = dp.parse(argument)
    if result:
        return result
    else:
        raise ValueError(f"{argument} does not match with any format.")
