# -*- coding: utf-8 -*-

"""
Checks and automatically fixes KRL (KUKA Robot Language) code.
"""

import os
from argparse import ArgumentParser, Action

import krllint
from .tools import get_parameters
from .parameters import Parameters
from .rules import RULES
from .reporter import Message


class Linter:
    def __init__(self, cli_args=None, config=None):
        if cli_args:
            self.cli_args = cli_args
        else:
            self.cli_args = _parse_args()

        if self.cli_args.generate_config:
            _create_configuration()

        if config:
            self.config = config
        else:
            self.config = _load_configuration(self.cli_args.config)

        self.extensions = (".src", ".dat", ".sub")

        self._parameters = Parameters(self.config)
        self._reporter = self.config.REPORTER()

    def lint(self):
        for target in self.cli_args.target:
            target = os.path.expanduser(target)
            if os.path.isdir(target):
                self._lint_directory(target)
            else:
                self._lint_file(target)

            self._reporter.finalize()

    def _lint_directory(self, dirname):
        for dirpath, _, filenames in os.walk(dirname):
            for filename in sorted(filter(
                    lambda file: file.endswith(self.extensions), filenames)):
                self._lint_file(os.path.join(dirpath, filename))

    def _lint_file(self, filename):
        self._reporter.start_file(filename)

        with open(filename) as content:
            lines = content.readlines()
            self._parameters.start_new_file(filename, lines)

        for _ in self._parameters:
            self._run_checkers(RULES["common"])

            if self._parameters.is_code:
                self._run_checkers(RULES["code"])

            if self._parameters.is_comment:
                self._run_checkers(RULES["comment"])

        self._reporter.finalize_file()

        if self.cli_args.fix:
            self._fix_file(filename)

    def _run_checkers(self, rules):
        for rule in rules:
            self._check_result(self._run_check(rule), rule)

    def _fix_file(self, filename):
        with open(filename, "w") as content:
            content.writelines(self._parameters.lines)

    def _check_result(self, results, checker):
        if results is None:
            return

        for result in results:
            _, _, code, _ = result
            if code in self.config.DISABLE:
                continue

            self._reporter.report(self._build_message(result))

            if self.cli_args.fix:
                self._fix_line(checker)

    def _build_message(self, result):
        category, column, code, message = result
        return Message(
            category, code, self._parameters.line_number, column, message)

    def _fix_line(self, checker):
        self._parameters.line = self._run_fix(checker)

    def _run_check(self, checker):
        return self._run_method(checker.lint)

    def _run_fix(self, checker):
        return self._run_method(checker.fix)

    def _run_method(self, method):
        parameters = []
        for parameter in get_parameters(method):
            if parameter == "self":
                continue
            parameters.append(getattr(self._parameters, parameter))

        return method(*parameters)


def _create_arg_parser():
    class TargetAction(Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if namespace.generate_config and not values:
                setattr(self, self.dest, [])
                namespace.target = []
            elif values:
                setattr(self, self.dest, values)
                namespace.target = values
            else:
                parser.error(
                    f"the following arguments are required: {self.dest}")


    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {krllint.__version__}")
    parser.add_argument("--config",
                        help="configuration file location")
    parser.add_argument("--generate-config", action="store_true",
                        help="Generates configuration file at current location")
    parser.add_argument("--fix", action="store_true",
                        help="automatically fix the given inputs")
    parser.add_argument("target", action=TargetAction, nargs="*",
                        help="file or folder to lint")

    return parser


def _parse_args():
    return _create_arg_parser().parse_args()


DEFAULT_CONFIG_NAME = "config.py"


def _create_configuration():
    from shutil import copyfile

    source = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIG_NAME)
    destination = f"./krllint.{DEFAULT_CONFIG_NAME}"

    if os.path.exists(destination):
        raise Exception(f"Configuration file already exists ({destination})!")

    try:
        copyfile(source, destination)
    except:
        raise Exception("Configuration file could not be created!")


def _load_configuration(filename=None):
    from importlib.util import spec_from_file_location, module_from_spec

    config_files = [
        filename,
        f"./krllint.{DEFAULT_CONFIG_NAME}",
        os.path.expanduser(f"~/.config/krllint.{DEFAULT_CONFIG_NAME}"),
        os.path.join(os.path.dirname(__file__), DEFAULT_CONFIG_NAME)
    ]

    for config_file in config_files:
        if config_file and os.path.exists(config_file):
            spec = spec_from_file_location("config", config_file)
            config = module_from_spec(spec)
            spec.loader.exec_module(config)
            return config

    raise Exception("It could not be found any configuration file!")
