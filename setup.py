from setuptools import setup, find_packages

import krllint

with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name="krllint",
    version=krllint.__version__,
    author="Daniel Braunwarth",
    author_email="d4nuu8@gmail.com",
    license="MIT",
    description="KRL code checker",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/d4nuu8/krllint",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "krllint = krllint.__main__:main"
        ]
    },
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
    ]
)
