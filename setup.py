from setuptools import setup, find_packages

setup(
    name="toomtam_agent",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
) 