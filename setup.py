from setuptools import setup, find_packages

setup(
    name="discogs",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "discogs = discogs.main:app"
        ]
    },
    install_requires=[
        "typer[all]",
        "rich",
        "pandas",
        "requests"
    ]
)