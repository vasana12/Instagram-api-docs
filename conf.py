import os
import sys
sys.path.insert(0, os.path.abspath("."))

project = 'datacast-instagram-api'
copyright = '2022, Jae young Kim <wodud6349@gmail.com>'
author = 'Jae young Kim <wodud6349@gmail.com>'

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme"
]

myst_enable_extensions = [
    "colon_fence",
]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv']
html_static_path = ['_static']
templates_path = ['_templates']
html_theme = 'sphinx_rtd_theme'
