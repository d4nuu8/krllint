# -*- coding: utf-8 -*-

from unittest import TestCase
from importlib import reload

from krllint import config
from krllint.reporter import Category, MemoryReporter
from krllint.linter import _create_arg_parser, Linter

class IndentationCheckerTestCase(TestCase):
    TEST_INPUT = [
        "IF foo THEN\n",
        "      bar\n",
        "ENDIF\n",
        "\n",
        "   ;FOLD PTP;%{PE}",
        "   ;ENDFOLD"
    ]

    FIXED_INPUT = [
        "IF foo THEN\n",
        "   bar\n",
        "ENDIF\n",
        "\n",
        ";FOLD PTP;%{PE}",
        ";ENDFOLD"
    ]

    def test_rule_without_fix(self):
        cli_args = _create_arg_parser().parse_args(["test_rule_without_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        linter = Linter(cli_args, config)
        lines, reporter = linter.lint_lines("test_rule_without_fix", self.TEST_INPUT)

        self.assertEqual(reporter.found_issues[Category.CONVENTION], 0)
        self.assertEqual(reporter.found_issues[Category.REFACTOR], 0)
        self.assertEqual(reporter.found_issues[Category.WARNING], 3)
        self.assertEqual(reporter.found_issues[Category.ERROR], 0)
        self.assertEqual(reporter.found_issues[Category.FATAL], 0)

        self.assertEqual(lines, self.TEST_INPUT)

        self.assertEqual(reporter.messages[0].line_number, 1)
        self.assertEqual(reporter.messages[0].column, 6)
        self.assertEqual(reporter.messages[0].message, "wrong indentation (found 6 spaces, exptected 3)")
        self.assertEqual(reporter.messages[0].code, "bad-indentation")

        self.assertEqual(reporter.messages[1].line_number, 4)
        self.assertEqual(reporter.messages[1].column, 3)
        self.assertEqual(reporter.messages[1].message, "wrong indentation (found 3 spaces, exptected 0)")
        self.assertEqual(reporter.messages[1].code, "bad-indented-inline-form")

        self.assertEqual(reporter.messages[2].line_number, 5)
        self.assertEqual(reporter.messages[2].column, 3)
        self.assertEqual(reporter.messages[2].message, "wrong indentation (found 3 spaces, exptected 0)")
        self.assertEqual(reporter.messages[2].code, "bad-indented-inline-form")

    def test_rule_with_fix(self):
        cli_args = _create_arg_parser().parse_args(["--fix", "test_rule_with_fix"])
        reload(config)
        config.REPORTER = MemoryReporter
        linter = Linter(cli_args, config)
        lines, _ = linter.lint_lines("test_rule_with_fix", self.TEST_INPUT)

        self.assertEqual(lines, self.FIXED_INPUT)
