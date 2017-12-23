# -*- coding: utf-8 -*-
DESCRIPTION = (
    'A python library to read and write structured data in csv, zipped csv ' +
    'format and to/from databases' +
    ''
)
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary'
]
intersphinx_mapping = {
    'pyexcel': ('http://pyexcel.readthedocs.io/en/latest/', None),
}
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'pyexcel-io'
copyright = u'2015-2017 Onni Software Ltd.'
version = '0.5.5'
release = '0.5.5'
exclude_patterns = []
pygments_style = 'sphinx'
html_theme = 'default'


def setup(app):
    app.add_stylesheet('theme_overrides.css')


html_static_path = ['_static']
htmlhelp_basename = 'pyexcel-iodoc'
latex_elements = {}
latex_documents = [
    ('index', 'pyexcel-io.tex',
     'pyexcel-io Documentation',
     'Onni Software Ltd.', 'manual'),
]
man_pages = [
    ('index', 'pyexcel-io',
     'pyexcel-io Documentation',
     [u'Onni Software Ltd.'], 1)
]
texinfo_documents = [
    ('index', 'pyexcel-io',
     'pyexcel-io Documentation',
     'Onni Software Ltd.', 'pyexcel-io',
     DESCRIPTION,
     'Miscellaneous'),
]
