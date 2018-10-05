# -*- coding: utf-8 -*-

from abc import ABC, abstractclassmethod

class BaseReporter(ABC):
    def __init__(self):
        self._filename = None
        self._first_message = True

    def start_file(self, filename):
        self._filename = filename
        self._first_message = True

    def report(self, message):
        category, *_ = message

        if self._first_message:
            self.handle_new_file(self._filename)
        self._first_message = False

        handle = getattr(self, "handle_" + category.name.lower())
        handle(message[1:])

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
        line_number, column, code, text = message
        print(f"{line_number + 1}:{column + 1}: {text} [{code}]")


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
        line_number, column, code, text = message
        print(f"{line_number + 1}:{column + 1}: {cls._colorize(text, style)} [{code}]")

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
