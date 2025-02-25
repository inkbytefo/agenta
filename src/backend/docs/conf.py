"""
Configuration file for the Sphinx documentation builder.
"""
import os
import sys

# Add the project source directory to the Python path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'CrewAI VSCode Extension'
copyright = '2025'
author = 'Development Team'
release = '0.1.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',  # Automatically include docstrings
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',  # Add links to highlighted source code
    'sphinx.ext.githubpages',  # Generate .nojekyll file for GitHub Pages
    'sphinx.ext.intersphinx',  # Link to other project's documentation
    'sphinx_autodoc_typehints',  # Show type hints in documentation
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# AutoDoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Theme settings
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False
}

# Output settings
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'crewai': ('https://docs.crewai.com', None),
}

# Generate API documentation
def setup(app):
    """Set up Sphinx application"""
    # Add any additional setup if needed
    pass