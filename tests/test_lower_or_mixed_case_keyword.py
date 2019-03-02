# -*- coding: utf-8 -*-

from unittest import TestCase
from importlib import reload

from krllint import config
from krllint.reporter import Category, MemoryReporter
from krllint.linter import _create_arg_parser, Linter

class LowerOrMixedCaseKeywordTestCase(TestCase):
    TEST_INPUT = ["If\n"]
    FIXED_INPUT = ["IF\n"]

    def test_rule_without_fix(self):
        cli_args = _create_arg_parser().parse_args(["test_rule_without_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        linter = Linter(cli_args, config)
        lines, reporter = linter.lint_lines("test_rule_without_fix", self.TEST_INPUT)

        self.assertEqual(reporter.found_issues[Category.CONVENTION], 0)
        self.assertEqual(reporter.found_issues[Category.REFACTOR], 0)
        self.assertEqual(reporter.found_issues[Category.WARNING], 1)
        self.assertEqual(reporter.found_issues[Category.ERROR], 0)
        self.assertEqual(reporter.found_issues[Category.FATAL], 0)

        self.assertEqual(lines, self.TEST_INPUT)

        self.assertEqual(reporter.messages[0].line_number, 0)
        self.assertEqual(reporter.messages[0].column, 0)
        self.assertEqual(reporter.messages[0].message, "lower or mixed case keyword")
        self.assertEqual(reporter.messages[0].code, "wrong-case-keyword")

    def test_rule_with_fix(self):
        cli_args = _create_arg_parser().parse_args(["--fix", "test_rule_with_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        linter = Linter(cli_args, config)
        lines, _ = linter.lint_lines("test_rule_with_fix", self.TEST_INPUT)

        self.assertEqual(lines, self.FIXED_INPUT)
