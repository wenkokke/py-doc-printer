# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

import sphinx_bootstrap_theme

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.


sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "doc-printer"
copyright = "2022, Wen Kokke"
author = "Wen Kokke"

# The full version, including alpha/beta/rc tags
release = "0.9.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The default options for autodoc directives. They are applied to all
# autodoc directives automatically. It must be a dictionary which maps
# option names to the values. For example:
autodoc_default_options = {
    "undoc-members": True,
}

# This value controls the format of typehints.
autodoc_typehints = "signature"
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True

autodoc_type_aliases = {
    "DocLike": "DocLike",
    "Token": "Token",
    "TokenStream": "TokenStream",
    "TokenBuffer": "TokenBuffer",
    "OnEmit": "OnEmit",
}

# -- Options for HTML output -------------------------------------------------

html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_theme_options = {
    "navbar_title": "Pretty Printer",
    "navbar_sidebarrel": False,
    "navbar_pagenav": False,
}
