from setuptools import setup, find_packages

setup(
    name="twins",
    version="100.2",
    description="Command-line interface to Univ. of Tsukuba's course registration system",
    load_description="",
    url="https://github.com/coins13/twins",
    scripts=["bin/twins"],
    install_requires=["pyquery", "requests", "prettytable", "sqlalchemy"],
    packages=find_packages(),
    classfiers = [
        "Operating System :: POSIX",
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Utilities"
    ]
)
