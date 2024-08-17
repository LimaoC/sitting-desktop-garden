# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

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


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = "piccolo_theme"
html_static_path = ["_static"]
