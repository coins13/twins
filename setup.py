from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="twins",
    version="100.0",
    description="A command line utility for coins",
    load_description=long_description,
    url="http://github.com/coins13/twins",
    py_modules=find_packages(),
    scripts=["bin/twins"],
    install_requires=open("requirements.txt").read().split('\n'),
    packages=find_packages(),
    classfiers = [
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Utilities"
    ]
)
