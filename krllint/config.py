# -*- coding: utf-8 -*-

"""
krllint configuration
"""

from krllint.reporter import TextReporter, ColorizedTextReporter

# Character to be used for indentation
INDENT_CHAR = " "

# Number of indentation characters to be used per indentation level
INDENT_SIZE = 3

# Messages to be disabled (identified by their id e.g bad-indentation)
DISABLE = []

# Reporter to be used to display results
# Available reporters are:
#   - TextReporter
#   - ColorizedTextReporter
REPORTER = ColorizedTextReporter
