#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from krllint import Linter

def main():
    try:
        linter = Linter()
        linter.lint()
    except Exception as ex:
        print(f"Error: {str(ex)}")

if __name__ == "__main__":
    main()
