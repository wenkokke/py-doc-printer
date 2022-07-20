"""
Py-PrettyPrinter
"""

from setuptools import setup

import os


with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    LONG_DESCRIPTION = f.read()


setup(
    name="prettyprinter",
    version="0.1.1",
    maintainer="Wen Kokke",
    maintainer_email="me@wen.works",
    author="Wen Kokke",
    author_email="me@wen.works",
    url="https://github.com/wenkokke/py-prettyprinter",
    license="MIT",
    platforms=["any"],
    python_requires=">=3.3",
    description="Formatter for Talon files",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Compilers",
        "Topic :: Text Processing :: Linguistic",
    ],
    packages=["prettyprinter"],
    project_urls={"Source": "https://github.com/wenkokke/py-prettyprinter"},
    install_requires=[
        "overrides",
        "more_itertools",
    ],
    package_data={"prettyprinter": ["py.typed"]},
)
