from setuptools import setup, find_packages

setup(
    name="dnestpy",
    version="0.1.0",
    description="Python package for manipulating dragonnest resources",
    author="Kalhartt",
    author_email="kalhartt@gmail.com",
    url="http://github.com/Yadnss/dnestpy",
    install_requires = ["pathlib"],
    packages=find_packages()
)
