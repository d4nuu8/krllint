# -*- coding: utf-8 -*-

import inspect


def get_parameters(method):
    return [parameter.name
            for parameter in inspect.signature(method).parameters.values()
            if parameter.kind == parameter.POSITIONAL_OR_KEYWORD]


def register_rule(rule):
    from .rules import RULES

    params = get_parameters(rule.lint)

    if params[1] == "line" and rule not in RULES["common"]:
        RULES["common"].append(rule())
    elif params[1] == "code_line" and rule not in RULES["code"]:
        RULES["code"].append(rule())
    elif params[1] == "comment_line" and rule not in RULES["comment"]:
        RULES["comment"].append(rule())

    return rule
