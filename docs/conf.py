# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from sphinx.application import Sphinx
sys.path.insert(0, os.path.abspath("../src/qudi/"))

project = "qudi-iqo-modules"
copyright = "2024, Ulm IQO"
author = "Ulm IQO"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# 'IPython.sphinxext.ipython_console_highlighting',
# 'nbsphinx',
# 'IPython.sphinxext.ipython_directive',
extensions = [
    'numpydoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest', 
    'sphinx_design',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon', 
    'autoapi.extension'
]


autoapi_dirs = [ '../src']
autoapi_type = 'python'               # Specify that we are documenting Python code
autoapi_generate_api_docs = True      # Automatically generate API docs
autoapi_add_toctree_entry = True      # Add entries to the TOC tree
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'imported-members'
]
autoapi_keep_files = True             # Keep generated .rst files for debugging
autoapi_root = 'api'                  # Root directory for generated API documentation


intersphinx_mapping = {
    "PySide2": (
        "https://doc.qt.io/qtforpython-5",
        None,
    ),  # This is broken, some bug with PySide2 (and PySide6). See https://bugreports.qt.io/browse/PYSIDE-2215
}
# 'lmfit': ('https://lmfit.github.io/lmfit-py/', None),

templates_path = ["templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

autosummary_generate = True
autosummary_ignore_module_all = False
autosummary_imported_members = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_logo = "../src/qudi/artwork/logo_qudi.ico"
html_theme_options = {
    "logo": {
        "text": "Qudi-IQO-MODULES",
        "image_dark": "../src/qudi/artwork/logo/logo_qudi.ico",
    },
    'dark_mode': True,
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    "navbar_persistent": ["theme-switcher", "search-button"],
    "footer_start": ["copyright", "sphinx-version"],
    "footer_end": ["theme-version"],
    "show_toc_level": 2,
    "show_nav_level": 4,
    "collapse_navigation": True,
    "sidebar_hide_name": False,
    'navigation_with_keys': False,  # See https://github.com/pydata/pydata-sphinx-theme/issues/1492
}
html_sidebars = {
    "**": ["sidebar-nav-bs", "sidebar-ethical-ads"]
}
html_static_path = ['_static']  # Normally defaults to '_static' but we don't have any static files.
html_css_files = [
    'custom.css',
]
default_dark_mode = False  # For sphinx_rtd_dark_mode. Dark mode needs tweaking so not defaulting to it yet.

numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_class_members_toctree = False

intersphinx_mapping = {
    'core': ('https://qudi-core-testing.readthedocs.io/en/george/', None),
}


def process_docstring(
    app,
    what,
    name,
    obj,
    options, 
    lines
):
    if what in {"module",'package'} :
        orig_lines = lines[:]
        new_lines = []
        for line in orig_lines:
            if 'Copyright' in line:
                break
            new_lines.append(line)

        lines[:] = new_lines
        if lines and lines[-1]:
            lines.append('')
         

def setup(sphinx):
    sphinx.connect("autodoc-process-docstring", process_docstring) 
   
