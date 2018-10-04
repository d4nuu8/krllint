# -*- coding: utf-8 -*-

import os
import shutil
import filecmp
from unittest import TestCase, main

from krllint.linter import _create_arg_parser, _load_configuration, Linter

class TestKrlLint(TestCase):
    def test_integration(self):
        test_dir = os.path.dirname(__file__)

        dirty_file = os.path.relpath(
            os.path.join(test_dir, "dirty.src"), os.getcwd())

        clean_file = os.path.relpath(os.path.join(
            test_dir, "clean.src"), os.getcwd())

        test_file = os.path.relpath(os.path.join(
            test_dir, "test.src"), os.getcwd())

        if os.path.exists(test_file):
            os.remove(test_file)
        shutil.copyfile(dirty_file, test_file)

        cli_args = _create_arg_parser().parse_args(["--fix", test_file])
        config = _load_configuration(cli_args.config)
        linter = Linter(cli_args, config)
        linter.lint()

        self.assertTrue(filecmp.cmp(test_file, clean_file))


if __name__ == "__main__":
    main()
