from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="twins",
    version="100.0",
    description="Command-line interface to Univ. of Tsukuba's course registration system",
    load_description=long_description,
    url="https://github.com/coins13/twins",
    py_modules=find_packages(),
    scripts=["bin/twins"],
    install_requires=open("requirements.txt").read().split('\n'),
    packages=find_packages(),
    classfiers = [
        "Operating System :: POSIX",
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Utilities"
    ]
)
