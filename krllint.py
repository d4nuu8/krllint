#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 Daniel Braunwarth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Checks and automatically fixes KRL (KUKA Robot Language) code.
"""

import os
import re
import inspect
from abc import ABC, abstractmethod

__version__ = "0.1.2"


CHECKERS = {"common": [], "code": [], "comment": []}

KEYWORDS = [
    "GLOBAL", "PUBLIC", "DEF", "END", "DEFFCT", "ENDFCT", "DEFDAT", "ENDDAT",
    "IN", "OUT", "IF", "THEN", "ELSE", "ENDIF", "FOR", "TO", "STEP", "ENDFOR",
    "LOOP", "ENDLOOP", "REPEAT", "UNTIL", "SWTICH", "CASE", "DEFAULT",
    "ENDSWITCH", "WAIT", "SEC", "WHILE", "ENDWHILE", "SIGNAL", "CONST", "ANIN",
    "ANOUT", "ON", "OFF", "DELAY", "MINIMUM", "MAXIMUM", "CONTINUE", "EXIT",
    "GOTO", "HALT", "RETURN", "RESUME", "PULSE", "BRAKE", "INTERRUPT", "DECL",
    "WHEN", "DO", "ENABLE", "DISABLE", "TRIGGER", "DISTANCE", "PATH", "ONSTART",
    "DELAY", "PTP", "LIN", "CIRC", "PTP_REL", "LIN_REL", "SPLINE", "ENDSPLINE",
    "SPL", "SPTP", "SLIN", "SCIRC", "TIME_BLOCK", "START", "PART", "END",
    "NOT", "AND", "OR", "EXOR", "B_NOT", "B_AND", "B_OR", "B_EXOR"
]

BUILT_IN_TYPES = [
    "INT", "REAL", "CHAR", "FRAME", "POS", "E6POS", "AXIS", "E6AXIS", "STRUC",
    "ENUM"
]

OPERATORS = [
    "+", "-", "*", "/", ":", "=", "==", "<>", ">", "<", ">=", "<="
]

INDENT_IDENTIFIERS = [
    "IF", "ELSE", r"(?<!WAIT\s)FOR", "LOOP", "REPEAT", "SWITCH", "CASE",
    "DEFAULT", "WHILE"
]

UNINDENT_IDENTIFIERS = [
    "ELSE", "ENDIF", "ENDFOR", "ENDLOOP", "UNTIL", "CASE", "DEFAULT",
    "ENDSWITCH", "ENDWHILE"
]


def _get_parameters(method):
    return [parameter.name
            for parameter in inspect.signature(method).parameters.values()
            if parameter.kind == parameter.POSITIONAL_OR_KEYWORD]


def register_checker(checker):
    params = _get_parameters(checker.lint)

    if params[1] == "line" and checker not in CHECKERS["common"]:
        CHECKERS["common"].append(checker())
    elif params[1] == "code_line" and checker not in CHECKERS["code"]:
        CHECKERS["code"].append(checker())
    elif params[1] == "comment_line" and checker not in CHECKERS["comment"]:
        CHECKERS["comment"].append(checker())

    return checker


class BaseChecker(ABC):
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
          - unique issue identifier (str)
          - a short description of the found issue (str)
          - the column in the checked line where the issue where found (int)
        """
        pass

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
        pass


################################################################################
# Checkers
################################################################################


@register_checker
class TrailingWhitespace(BaseChecker):
    def lint(self, line):
        line = line.rstrip("\r\n")
        stripped_line = line.rstrip()
        if line != stripped_line:
            yield ("trailing-whitespace",
                   "trailing whitespace",
                   len(stripped_line))

    def fix(self, line):
        return line.strip() + "\n"


@register_checker
class TabsChecker(BaseChecker):
    def lint(self, line):
        if "\t" in line:
            yield "mixed-indentation", "line contains tab(s)", 0

    def fix(self, line, indent_char, indent_size):
        return line.replace("\t", indent_char * indent_size)


@register_checker
class IndentationChecker(BaseChecker):
    INDENT_PATTERN = re.compile(
        r"(?<!#)(\b(?:" + "|".join(INDENT_IDENTIFIERS) + r")\b)",
        re.IGNORECASE)

    UNINDENT_PATTERN = re.compile(
        r"(?<!#)(\b(?:" + "|".join(UNINDENT_IDENTIFIERS) + r")\b)",
        re.IGNORECASE)

    def __init__(self):
        self._filename = None
        self._indent_level = 0
        self._indent_next_line = False

    def lint(self, line, filename, code_line, indent_size):
        if self._filename != filename:
            self._start_new_file(filename)

        if self._indent_next_line:
            self._increase_indent_level()

        if self._is_unindentation_needed(code_line):
            self._decrease_indent_level()

        if self._is_indentation_needed(code_line):
            self._indent_next_line = True

        stripped_line = line.lstrip()

        if not stripped_line:
            return

        indent = len(line) - len(stripped_line)
        indent_wanted = self._indent_level * indent_size

        if indent != indent_wanted:
            yield ("bad-indentation",
                   (f"wrong indentation (found {indent} spaces, "
                    f"exptected {indent_wanted})"),
                   indent)

    def fix(self, line, indent_size, indent_char):
        return indent_char * (self._indent_level * indent_size) + line.lstrip()


    def _start_new_file(self, filename):
        self._filename = filename
        self._indent_level = 0
        self._indent_next_line = False

    @staticmethod
    def _is_indentation_needed(code_line):
        return not IndentationChecker.INDENT_PATTERN.search(code_line) is None

    @staticmethod
    def _is_unindentation_needed(code_line):
        return not IndentationChecker.UNINDENT_PATTERN.search(code_line) is None

    def _increase_indent_level(self):
        self._indent_level += 1
        self._indent_next_line = False

    def _decrease_indent_level(self):
        self._indent_level -= 1
        if self._indent_level < 0:
            self._indent_level = 0


@register_checker
class ExtraneousWhitespace(BaseChecker):
    WHITESPACE_PATTERN = re.compile(r"(?<=\S)\s{2,}")

    def lint(self, code_line):
        for match in self.WHITESPACE_PATTERN.finditer(code_line.strip()):
            yield ("superfluous-whitespace",
                   "superfluous whitespace",
                   match.start())

    def fix(self, code_line, comment_line):
        return (self.WHITESPACE_PATTERN.sub(lambda _: " ", code_line) +
                ((";" + comment_line) if comment_line else ""))


class BaseMixedCaseChecker(BaseChecker):
    @property
    def pattern(self):
        return re.compile(r"", re.IGNORECASE)

    def lint(self, code_line):
        for match in self.pattern.finditer(code_line):
            if not str(match.group(1)).isupper():
                yield match.start()

    def fix(self, code_line, comment_line):
        return (self.pattern.sub(self._fix_match, code_line) +
                ((";" + comment_line) if comment_line else ""))

    @staticmethod
    def _fix_match(match):
        target = str(match.group(1))
        return target if target.isupper() else target.upper()


@register_checker
class LowerOrMixedCaseKeyword(BaseMixedCaseChecker):
    @property
    def pattern(self):
        return re.compile(r"(?<!#)(\b(?:" + "|".join(KEYWORDS) + r")\b)",
                          re.IGNORECASE)

    def lint(self, code_line):
        for column in super().lint(code_line):
            yield ("wrong-case-keyword",
                   "lower or mixed case keyword",
                   column)


@register_checker
class LowerOrMixedCaseBuiltInType(BaseMixedCaseChecker):
    @property
    def pattern(self):
        return re.compile(r"(?<!#)(\b(?:" + "|".join(BUILT_IN_TYPES) + r")\b)",
                          re.IGNORECASE)

    def lint(self, code_line):
        for column in super().lint(code_line):
            yield  ("wrong-case-type",
                    "lower or mixed case built-in type",
                    column)


################################################################################
# Framework
################################################################################


class CheckerParameters:
    def __init__(self, config):
        self._lines = []
        self._next = 0
        self._filename = None

        for attr, value in config.__dict__.items():
            if not attr.startswith("_"):
                setattr(self, attr.lower(), value)

    def __iter__(self):
        return self

    def __next__(self):
        if self._next == self.total_lines:
            raise StopIteration
        else:
            self._next += 1
            return self.lines[self.line_number]

    def start_new_file(self, filename, lines):
        self._lines = lines
        self._next = 0
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    @property
    def lines(self):
        return self._lines

    @property
    def line_number(self):
        return self._next - 1

    @property
    def total_lines(self):
        return len(self._lines)

    @property
    def line(self):
        return (self.lines[self.line_number]
                if self.line_number < self.total_lines
                else None)

    @line.setter
    def line(self, value):
        self.lines[self.line_number] = value

    @property
    def code_line(self):
        return self.line.split(";", 1)[0]

    @property
    def comment_line(self):
        if len(self.line.split(";")) == 2:
            return self.line.split(";", 1)[1]

        if (self.line.split("&")) == 2:
            return self.line.split("&", 1)[1]

        return ""

    @property
    def is_code(self):
        return (not self.line.lstrip().startswith(";") and
                not self.line.lstrip().startswith("&"))

    @property
    def is_comment(self):
        return any(char in self.line for char in [";", "&"])


class Reporter:
    ERROR_CODE_PATTERN = re.compile(r"^[EW]\d+")

    def __init__(self):
        self._filename = None

    def start_file(self, filename):
        self._filename = filename
        print(filename)

    def error(self, line_number, result):
        code, text, column = result
        print(f"{line_number + 1}:{column + 1}: {text} [{code}]")


class Linter:
    def __init__(self, options, config):
        self.options = options
        self.config = config
        self.extensions = (".src", ".dat", ".sub")

        self._parameters = CheckerParameters(config)
        self._reporter = Reporter()

    checkers = CHECKERS

    def lint(self):
        for target in self.options.target:
            if os.path.isdir(target):
                self._lint_directory(target)
            else:
                self._lint_file(target)

    def _lint_directory(self, dirname):
        for dirpath, _, filenames in os.walk(dirname):
            for filename in sorted(filter(
                    lambda file: file.endswith(self.extensions), filenames)):
                self._lint_file(os.path.join(dirpath, filename))

    def _lint_file(self, filename):
        self._reporter.start_file(filename)

        with open(filename) as content:
            lines = content.readlines()
            self._parameters.start_new_file(filename, lines)

        for _ in self._parameters:
            self._run_checkers(self.checkers["common"])

            if self._parameters.is_code:
                self._run_checkers(self.checkers["code"])

            if self._parameters.is_comment:
                self._run_checkers(self.checkers["comment"])

        if self.options.fix:
            self._fix_file(filename)

    def _run_checkers(self, checkers):
        for checker in checkers:
            self._check_result(self._run_check(checker), checker)

    def _fix_file(self, filename):
        with open(filename, "w") as content:
            content.writelines(self._parameters.lines)

    def _check_result(self, results, checker):
        if results is None:
            return

        for result in results:
            code, _, _ = result
            if code in self.config.DISABLE:
                continue

            self._reporter.error(self._parameters.line_number, result)

            if self.options.fix:
                self._fix_line(checker)

    def _fix_line(self, checker):
        self._parameters.line = self._run_fix(checker)

    def _run_check(self, checker):
        return self._run_method(checker.lint)

    def _run_fix(self, checker):
        return self._run_method(checker.fix)

    def _run_method(self, method):
        parameters = []
        for parameter in _get_parameters(method):
            if parameter == "self":
                continue
            parameters.append(getattr(self._parameters, parameter))

        return method(*parameters)


def _create_arg_parser():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--config",
                        help="configuration file location")
    parser.add_argument("--fix", action="store_true",
                        help="automatically fix the given inputs")
    parser.add_argument("target", nargs="+", help="file or folder to lint")

    return parser


def _parse_args():
    return _create_arg_parser().parse_args()

def _load_configuration(filename=None):
    from importlib.util import spec_from_file_location, module_from_spec

    config_files = [
        os.path.expanduser("~/.config/krllint.conf.py"),
        filename, "./krllint.conf.py"
    ]

    for config_file in config_files:
        if config_file and os.path.exists(config_file):
            spec = spec_from_file_location("config", config_file)
            config = module_from_spec(spec)
            spec.loader.exec_module(config)
            return config

    raise Exception("It could not be found any configuration file!")


def _main():
    cli_args = _parse_args()
    config = _load_configuration(cli_args.config)
    linter = Linter(cli_args, config)

    linter.lint()


if __name__ == "__main__":
    _main()
