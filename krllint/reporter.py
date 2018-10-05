# -*- coding: utf-8 -*-

from abc import ABC, abstractclassmethod
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

    def start_file(self, filename):
        self._filename = filename
        self._messages = []

    def finish_file(self):
        if self._messages:
            self.handle_new_file(self._filename)

            for message in self._messages:
                handle = getattr(
                    self, "handle_" + message.category.name.lower())
                handle(message)

        self._filename = None

    def report(self, message):
        self._messages.append(message)

    @abstractclassmethod
    def handle_new_file(cls, filename):
        pass

    @abstractclassmethod
    def handle_convention(cls, message):
        pass

    @abstractclassmethod
    def handle_refactor(cls, message):
        pass

    @abstractclassmethod
    def handle_warning(cls, message):
        pass

    @abstractclassmethod
    def handle_error(cls, message):
        pass

    @abstractclassmethod
    def handle_fatal(cls, message):
        pass


class TextReporter(BaseReporter):
    @classmethod
    def handle_new_file(cls, filename):
        print(f"***** {filename}")

    @classmethod
    def handle_convention(cls, message):
        cls.handle_message(message)

    @classmethod
    def handle_refactor(cls, message):
        cls.handle_message(message)

    @classmethod
    def handle_warning(cls, message):
        cls.handle_message(message)

    @classmethod
    def handle_error(cls, message):
        cls.handle_message(message)

    @classmethod
    def handle_fatal(cls, message):
        cls.handle_message(message)

    @classmethod
    def handle_message(cls, message):
        print(
            f"{message.line_number + 1}:{message.column + 1}: "
            f"{message.message} [{message.code}]")


class ColorizedTextReporter(BaseReporter):
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

    @classmethod
    def handle_new_file(cls, filename):
        print(cls._colorize(f"***** {filename}", cls.SEPERATOR))

    @classmethod
    def handle_convention(cls, message):
        cls.handle_message(message, cls.CONVENTION)

    @classmethod
    def handle_refactor(cls, message):
        cls.handle_message(message, cls.REFACTOR)

    @classmethod
    def handle_warning(cls, message):
        cls.handle_message(message, cls.WARNING)

    @classmethod
    def handle_error(cls, message):
        cls.handle_message(message, cls.ERROR)

    @classmethod
    def handle_fatal(cls, message):
        cls.handle_message(message, cls.FATAL)

    @classmethod
    def handle_message(cls, message, style):
        print(
            f"{message.line_number + 1}:{message.column + 1}: "
            f"{cls._colorize(message.message, style)} [{message.code}]")

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
