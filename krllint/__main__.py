#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from krllint import Linter

def main():
    try:
        linter = Linter()
        linter.lint()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
