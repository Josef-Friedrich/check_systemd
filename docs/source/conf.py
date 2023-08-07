import sphinx_rtd_theme

# GLib.PGError: Could not connect: No such file or directory
# import check_systemd

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]
templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"

project = "check_systemd"
copyright = "2020, Josef Friedrich"
author = "Josef Friedrich"
# version = check_systemd.__version__
# release = check_systemd.__version__
version = '2.3.1'
release = '2.3.1'
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False
html_static_path = []
htmlhelp_basename = "checksystemddoc"
autodoc_default_flags = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
]
napoleon_use_param = True
