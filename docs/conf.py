import os, sys
sys.path.insert(0, os.path.abspath('..'))

project = 'fjfnaranjo-bot'
copyright = '2021, Francisco José Fernández Naranjo'  # noqa
author = 'Francisco José Fernández Naranjo'
extensions = ['sphinx.ext.autodoc']
exclude_patterns = ['_build']

html_sidebars = { '**': ['globaltoc.html'] }
