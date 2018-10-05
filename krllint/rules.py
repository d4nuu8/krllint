# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import re

from .tools import register_rule
from .reporter import Category


RULES = {"common": [], "code": [], "comment": []}


class BaseRule(ABC):
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

@register_rule
class TrailingWhitespace(BaseRule):
    def lint(self, line):
        line = line.rstrip("\r\n")
        stripped_line = line.rstrip()
        if line != stripped_line:
            yield (Category.CONVENTION,
                   len(stripped_line),
                   "trailing-whitespace",
                   "trailing whitespace")

    def fix(self, line):
        return line.strip() + "\n"


@register_rule
class MixedIndentation(BaseRule):
    def lint(self, line, indent_char):
        invalid_character = [" ", "\t"]
        invalid_character.remove(indent_char)

        if any(map(lambda char: char in line, invalid_character)):
            yield (Category.WARNING,
                   0,
                   "mixed-indentation",
                   "line contains tab(s)")

    def fix(self, line, indent_char, indent_size):
        return line.replace("\t", indent_char * indent_size)


@register_rule
class IndentationChecker(BaseRule):
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
            yield (Category.WARNING,
                   indent,
                   "bad-indentation",
                   (f"wrong indentation (found {indent} spaces, "
                    f"exptected {indent_wanted})"))

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


@register_rule
class ExtraneousWhitespace(BaseRule):
    WHITESPACE_PATTERN = re.compile(r"(?<=\S)\s{2,}")

    def lint(self, code_line):
        for match in self.WHITESPACE_PATTERN.finditer(code_line.strip()):
            yield (Category.CONVENTION,
                   match.start(),
                   "superfluous-whitespace",
                   "superfluous whitespace")

    def fix(self, code_line, comment_line):
        return (self.WHITESPACE_PATTERN.sub(lambda _: " ", code_line) +
                ((";" + comment_line) if comment_line else ""))


class BaseMixedCaseChecker(BaseRule):
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


@register_rule
class LowerOrMixedCaseKeyword(BaseMixedCaseChecker):
    @property
    def pattern(self):
        return re.compile(r"(?<!#)(\b(?:" + "|".join(KEYWORDS) + r")\b)",
                          re.IGNORECASE)

    def lint(self, code_line):
        for column in super().lint(code_line):
            yield (Category.WARNING,
                   column,
                   "wrong-case-keyword",
                   "lower or mixed case keyword")


@register_rule
class LowerOrMixedCaseBuiltInType(BaseMixedCaseChecker):
    @property
    def pattern(self):
        return re.compile(r"(?<!#)(\b(?:" + "|".join(BUILT_IN_TYPES) + r")\b)",
                          re.IGNORECASE)

    def lint(self, code_line):
        for column in super().lint(code_line):
            yield  (Category.WARNING,
                    column,
                    "wrong-case-type",
                    "lower or mixed case built-in type")
