# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import collections
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sitting-desktop-garden"
copyright = (
    "2024, Limao Chang, Mitchell Clark, Gabriel Field, Iain Jensen, David Ramsay"
)
author = "Limao Chang, Mitchell Clark, Gabriel Field, Iain Jensen, David Ramsay"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


sys.path.insert(0, os.path.abspath("../.."))

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.napoleon",
    "sphinxcontrib.apidoc",
]

templates_path = ["_templates"]
exclude_patterns = []

apidoc_module_dir = "../../client"
apidoc_output_dir = "api"

napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = "piccolo_theme"
html_static_path = ["_static"]

# -- Post process ------------------------------------------------------------


def remove_namedtuple_attrib_docstring(app, what, name, obj, skip, options):
    """Removes the auto-generated docstring for NamedTuple attributes.

    REF: https://stackoverflow.com/questions/61572220/python-sphinx-namedtuple-documentation
    """
    if type(obj) is collections._tuplegetter:
        return True
    return skip


def setup(app):
    app.connect("autodoc-skip-member", remove_namedtuple_attrib_docstring)
