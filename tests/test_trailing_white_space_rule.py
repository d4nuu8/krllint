# -*- coding: utf-8 -*-

from unittest import TestCase
from importlib import reload

from krllint import config
from krllint.reporter import Category, MemoryReporter
from krllint.linter import _create_arg_parser, Linter

class TrailingWhiteSpaceTestCase(TestCase):
    TEST_INPUT = ["INT someVariable   \n"]
    FIXED_INPUT = ["INT someVariable\n"]

    def test_rule_without_fix(self):
        cli_args = _create_arg_parser().parse_args(["test_rule_without_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        linter = Linter(cli_args, config)
        lines, reporter = linter.lint_lines("test_rule_without_fix", self.TEST_INPUT)

        self.assertEqual(reporter.found_issues[Category.CONVENTION], 1)
        self.assertEqual(reporter.found_issues[Category.REFACTOR], 0)
        self.assertEqual(reporter.found_issues[Category.WARNING], 0)
        self.assertEqual(reporter.found_issues[Category.ERROR], 0)
        self.assertEqual(reporter.found_issues[Category.FATAL], 0)

        self.assertEqual(lines, self.TEST_INPUT)

        self.assertEqual(reporter.messages[0].line_number, 0)
        self.assertEqual(reporter.messages[0].column, 16)
        self.assertEqual(reporter.messages[0].message, "trailing whitespace")
        self.assertEqual(reporter.messages[0].code, "trailing-whitespace")

    def test_rule_with_fix(self):
        cli_args = _create_arg_parser().parse_args(["--fix", "test_rule_with_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        linter = Linter(cli_args, config)
        lines, _ = linter.lint_lines("test_rule_with_fix", self.TEST_INPUT)

        self.assertEqual(lines, self.FIXED_INPUT)
