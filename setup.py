from setuptools import setup, find_packages

setup(
    name="swisscv",
    version="0.0.0",
    description="Swiss CV Generator (dev editable install)",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
