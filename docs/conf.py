import sphinx_rtd_theme
from importlib.metadata import version as get_version
from datetime import datetime

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]
templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"

project = "check_systemd"
copyright: str = f"2019-{datetime.now().year}, Josef Friedrich"
author = "Josef Friedrich"
version: str = get_version("check_systemd")
release: str = get_version("check_systemd")
language = "en"
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_static_path = []
htmlhelp_basename = "checksystemddoc"
autodoc_default_flags = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
]
