"""Sphinx configuration."""
project = "requestmodel"
author = "Jelmer Draaijer"
copyright = "2023, Jelmer Draaijer"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
