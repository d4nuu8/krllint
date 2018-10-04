# -*- coding: utf-8 -*-

class Parameters:
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
