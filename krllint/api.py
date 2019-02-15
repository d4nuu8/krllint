# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from .tools import get_parameters


RULES = {"common": [], "code": [], "comment": []}


class RuleMeta(ABCMeta):
    def __new__(cls, name, bases, namespace, **kwargs):
        instance = super().__new__(cls, name, bases, namespace, **kwargs)
        cls.__register_rule(instance)
        return instance

    @classmethod
    def __register_rule(cls, rule):
        params = get_parameters(rule.lint)

        if len(params) <= 1:
            return rule

        if params[1] == "line" and rule not in RULES["common"]:
            RULES["common"].append(rule())
        elif params[1] == "code_line" and rule not in RULES["code"]:
            RULES["code"].append(rule())
        elif params[1] == "comment_line" and rule not in RULES["comment"]:
            RULES["comment"].append(rule())

        return rule


class BaseRule(metaclass=RuleMeta):
    """
    Encapsulates a method to lint and a method to fix a possibly found issue.
    """
    @abstractmethod
    def lint(self):
        """
        Checks the code for issues.

        This method is dynamically called by class:: StyleChecker().
        Possible arguemts are:
          - All attributes of class:: CheckerParameters
          - All attributes defined in the configuration file

        This method must yield a tuple of the following values for each found
        issue:
          - Issue category (Category)
          - the column in the checked line where the issue where found (int)
          - unique issue identifier (str)
          - a short description of the found issue (str)
        """

    @abstractmethod
    def fix(self):
        """
        Fixes the found issue.

        This method is dynamically called by class:: StyleChecker().
        Possible arguemts are:
          - All attributes of class:: CheckerParameters
          - All attributes defined in the configuration file

        This method must return the fixed line.
        """
