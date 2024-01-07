#!/usr/bin/env python

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requirements = [
    "coloredlogs",
    "PyYAML",
]

if __name__ == "__main__":
    setuptools.setup(
        name="gmdm",
        version="0.1.8",
        author="Kenan Masri",
        author_email="kenanmasri@outlook.com",
        description="The GMDM CLI tool for managing dependencies of GameMaker projects and files.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/knno/gmdm",
        project_urls={
            "Bug Tracker": "https://github.com/knno/gmdm/issues",
        },
        entry_points='''[console_scripts]\ngmdm=gmdm.cli:main''',
        install_requires=install_requirements,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        python_requires=">=3.11",
    )
