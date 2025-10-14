from setuptools import setup, find_packages
setup(
    name="swiss-cv-generator",
    version="0.0.1",
    description="Swiss CV Generator (dev editable install)",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pydantic",
        "pandas",
        "requests",
        "python-dotenv",
    ],
)
