# setup.py

from setuptools import setup, find_packages

setup(
    name="discogs",
    version="1.0.0",
    description="Discogs Data Processor CLI",
    author="ofurkancoban",
    author_email="ofurkancoban@gmail.com",
    url="https://github.com/ofurkancoban/DiscogsCLI",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all]",
        "rich",
        "requests",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "discogs=discogs.main:app"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)