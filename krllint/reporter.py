#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

class Reporter:
    ERROR_CODE_PATTERN = re.compile(r"^[EW]\d+")

    def __init__(self):
        self._filename = None

    def start_file(self, filename):
        self._filename = filename
        print(filename)

    @staticmethod
    def error(line_number, result):
        code, text, column = result
        print(f"{line_number + 1}:{column + 1}: {text} [{code}]")
