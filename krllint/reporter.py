# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from collections import namedtuple
from enum import Enum


class Category(Enum):
    CONVENTION = 1
    REFACTOR = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5
    SEPERATOR = 6


Message = namedtuple(
    "Message", ["category", "code", "line_number", "column", "message"])


class BaseReporter(ABC):
    def __init__(self):
        self._filename = None
        self._messages = []
        self.found_issues = {
            Category.CONVENTION: 0,
            Category.REFACTOR: 0,
            Category.WARNING: 0,
            Category.ERROR: 0,
            Category.FATAL: 0
        }

    def start_file(self, filename):
        self._filename = filename
        self._messages = []

    def finalize_file(self):
        if self._messages:
            self.handle_new_file()

            for message in self._messages:
                handle = getattr(
                    self, "handle_" + message.category.name.lower())
                handle(message)

        self._filename = None

    @abstractmethod
    def finalize(self):
        pass

    def report(self, message):
        self.found_issues[message.category] += 1
        self._messages.append(message)

    @abstractmethod
    def handle_new_file(self):
        pass

    @abstractmethod
    def handle_convention(self, message):
        pass

    @abstractmethod
    def handle_refactor(self, message):
        pass

    @abstractmethod
    def handle_warning(self, message):
        pass

    @abstractmethod
    def handle_error(self, message):
        pass

    @abstractmethod
    def handle_fatal(self, message):
        pass

    @property
    def max_line_number(self):
        return len(str(max(
            self._messages,
            key=lambda message: message.line_number).line_number))

    @property
    def max_column(self):
        return len(str(max(
            self._messages,
            key=lambda message: message.column).column))

class TextReporter(BaseReporter):
    def handle_new_file(self):
        print(f"***** {self._filename}")

    def finalize(self):
        print(20 * "-")
        print("Result:")
        print(f"{self.found_issues[Category.CONVENTION]} violated conventions")
        print(f"{self.found_issues[Category.REFACTOR]} possible refactorings")
        print(f"{self.found_issues[Category.WARNING]} found warnings")
        print(f"{self.found_issues[Category.ERROR]} found errors")
        print(f"{self.found_issues[Category.FATAL]} fatal errors")

    def handle_convention(self, message):
        self.handle_message(message)

    def handle_refactor(self, message):
        self.handle_message(message)

    def handle_warning(self, message):
        self.handle_message(message)

    def handle_error(self, message):
        self.handle_message(message)

    def handle_fatal(self, message):
        self.handle_message(message)

    def handle_message(self, message):
        print(
            f"{message.line_number + 1:>{self.max_line_number}}:"
            f"{message.column + 1:<{self.max_column}}: "
            f"{message.message} [{message.code}]")


class ColorizedTextReporter(TextReporter):
    PREFIX = "\033["
    END = "m"
    RESET = PREFIX + "0" + END

    STYLES = {
        "bold": "1",
        "italic": "3",
        "underline": "4",
        "inverse": "7"
    }

    COLORS = {
        "black": "30",
        "red": "31",
        "yellow": "33",
        "magenta": "35"
    }

    CONVENTION = (None, ["bold"])
    REFACTOR = ("magenta", ["bold"])
    WARNING = ("magenta", None)
    ERROR = ("red", ["bold"])
    FATAL = ("red", ["inverse", "bold"])
    SEPERATOR = ("yellow", ["inverse"])

    def __init__(self):
        super().__init__()
        from colorama import init
        init()

    def handle_new_file(self):
        print(self._colorize(f"***** {self._filename}", self.SEPERATOR))

    def handle_convention(self, message):
        self.handle_message(message, self.CONVENTION)

    def handle_refactor(self, message):
        self.handle_message(message, self.REFACTOR)

    def handle_warning(self, message):
        self.handle_message(message, self.WARNING)

    def handle_error(self, message):
        self.handle_message(message, self.ERROR)

    def handle_fatal(self, message):
        self.handle_message(message, self.FATAL)

    def handle_message(self, message, style):
        print(
            f"{message.line_number + 1:>{self.max_line_number}}:"
            f"{message.column + 1:<{self.max_column}}: "
            f"{self._colorize(message.message, style)} [{message.code}]")

    @classmethod
    def _colorize(cls, message, style):
        return cls._get_ansi_code(*style) + message + cls.RESET

    @classmethod
    def _get_ansi_code(cls, foreground=None, styles=None):
        code = []

        if foreground:
            code.append(cls.COLORS[foreground])
        if styles:
            for style in styles:
                code.append(cls.STYLES[style])

        if code:
            return cls.PREFIX + ";".join(code) + cls.END
        return ""
