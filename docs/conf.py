#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- General configuration ------------------------------------------------
needs_sphinx = '5.0.2'
numfig = True
extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.imgmath',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
#    'sphinx-jsonschema',
    'sphinx.ext.intersphinx']
templates_path = ['_templates']
from recommonmark.parser import CommonMarkParser
source_suffix = ['.rst', '.md']
source_parsers = {
		'.md': CommonMarkParser,
}

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'CIMHub'
copyright = '2017-2022, Battelle Memorial Institute'
author = 'Pacific Northwest National Laboratory'
version = '1.1.0'
release = '1.1.0'
language = 'en'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = True

html_theme = 'sphinx_rtd_theme'

html_static_path = ['java']
htmlhelp_basename = 'CIMHub'
latex_elements = {
}

latex_documents = [
    (master_doc, 'CIMHub.tex', 'CIMHub Documentation',
     'Pacific Northwest National Laboratory', 'manual'),
]


man_pages = [
    (master_doc, 'cimhub', 'CIMHub Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'CIMHub', 'CIMHub Documentation',
     author, 'CIMHub', 'Electric power system network model translation via IEC 61970 and 61968.',
     'Miscellaneous'),
]



