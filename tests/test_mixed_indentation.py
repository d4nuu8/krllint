# -*- coding: utf-8 -*-

from unittest import TestCase
from importlib import reload

from krllint import config
from krllint.reporter import Category, MemoryReporter
from krllint.linter import _create_arg_parser, Linter

class MixedIndentationTestCase(TestCase):
    TEST_INPUT_WITH_SPACES = [" bar\n"]
    TEST_INPUT_WITH_TABS = ["\tbar\n"]
    TEST_RESULT_WITH_SPACES = ["   bar\n"]
    TEST_RESULT_WITH_TABS = ["\tbar\n"]

    def test_rule_with_spaces_allowed(self):
        cli_args = _create_arg_parser().parse_args(["test_rule_with_spaces_allowed"])
        reload(config)
        config.REPORTER = MemoryReporter
        config.INDENT_CHAR = " "
        config.DISABLE = ["bad-indentation"]
        linter = Linter(cli_args, config)
        lines, reporter = linter.lint_lines("test_rule_with_spaces_allowed", self.TEST_INPUT_WITH_TABS)

        self.assertEqual(reporter.found_issues[Category.CONVENTION], 0)
        self.assertEqual(reporter.found_issues[Category.REFACTOR], 0)
        self.assertEqual(reporter.found_issues[Category.WARNING], 1)
        self.assertEqual(reporter.found_issues[Category.ERROR], 0)
        self.assertEqual(reporter.found_issues[Category.FATAL], 0)

        self.assertEqual(lines, self.TEST_INPUT_WITH_TABS)

        self.assertEqual(reporter.messages[0].line_number, 0)
        self.assertEqual(reporter.messages[0].column, 0)
        self.assertEqual(reporter.messages[0].message, "line contains tab(s)")
        self.assertEqual(reporter.messages[0].code, "mixed-indentation")

    def test_rule_with_tabs_allowed(self):
        cli_args = _create_arg_parser().parse_args(["test_rule_with_tabs_allowed"])
        reload(config)
        config.REPORTER = MemoryReporter
        config.INDENT_CHAR = "\t"
        config.DISABLE = ["bad-indentation"]
        linter = Linter(cli_args, config)
        lines, reporter = linter.lint_lines("test_rule_with_tabs_allowed", self.TEST_INPUT_WITH_SPACES)

        self.assertEqual(reporter.found_issues[Category.CONVENTION], 0)
        self.assertEqual(reporter.found_issues[Category.REFACTOR], 0)
        self.assertEqual(reporter.found_issues[Category.WARNING], 1)
        self.assertEqual(reporter.found_issues[Category.ERROR], 0)
        self.assertEqual(reporter.found_issues[Category.FATAL], 0)

        self.assertEqual(lines, self.TEST_INPUT_WITH_SPACES)

        self.assertEqual(reporter.messages[0].line_number, 0)
        self.assertEqual(reporter.messages[0].column, 0)
        self.assertEqual(reporter.messages[0].message, "line contains tab(s)")
        self.assertEqual(reporter.messages[0].code, "mixed-indentation")

    def test_rule_with_tabs_allowed_and_fix(self):
        cli_args = _create_arg_parser().parse_args(["--fix", "test_rule_with_tabs_allowed_and_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        config.INDENT_CHAR = "\t"
        config.INDENT_SIZE = 1
        config.DISABLE = ["bad-indentation"]
        linter = Linter(cli_args, config)
        lines, _ = linter.lint_lines("test_rule_with_tabs_allowed_and_fix", self.TEST_INPUT_WITH_SPACES)

        self.assertEqual(lines, self.TEST_RESULT_WITH_TABS)

    def test_rule_with_spaces_allowed_and_fix(self):
        cli_args = _create_arg_parser().parse_args(["--fix", "test_rule_with_spaces_allowed_and_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        config.INDENT_CHAR = " "
        config.INDENT_SIZE = 3
        config.DISABLE = ["bad-indentation"]
        linter = Linter(cli_args, config)
        lines, _ = linter.lint_lines("test_rule_with_spaces_allowed_and_fix", self.TEST_INPUT_WITH_TABS)

        self.assertEqual(lines, self.TEST_RESULT_WITH_SPACES)