from datetime import datetime
from importlib.metadata import version as get_version

import sphinx_rtd_theme  # type: ignore

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

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
autodoc_default_options = {
    # If set, autodoc will generate documention for the members of the target module, class or exception.
    "members": True,
    # This value selects if automatically documented members are sorted alphabetical (value 'alphabetical'), by member type (value 'groupwise') or by source order (value 'bysource'). The default is alphabetical.
    "member-order": "bysource",
    # If set, autodoc will also generate document for the members not having docstrings:
    "undoc-members": False,
    # If set, autodoc will also generate document for the private members (that is, those named like _private or __private)
    "private-members": False,
    # If set, autodoc will also generate document for the special members (that is, those named like __special__):
    "special-members": False,
    # For classes and exceptions, members inherited from base classes will be left out when documenting all members, unless you give the inherited-members option, in addition to members
    "inherited-members": False,
    # The automodule, autoclass and autoexception directives also support a flag option called show-inheritance. When given, a list of base classes will be inserted just below the class signature (when used with automodule, this will be inserted for every class that is documented in the module).
    "show-inheritance": False,
    # For modules, __all__ will be respected when looking for members unless you give the ignore-module-all flag option. Without ignore-module-all, the order of the members will also be the order in __all__.
    "ignore-module-all": False,
    # In an automodule directive with the members option set, only module members whose __module__ attribute is equal to the module name as given to automodule will be documented. This is to prevent documentation of imported classes or functions. Set the imported-members option if you want to prevent this behavior and document all available members. Note that attributes from imported modules will not be documented, because attribute documentation is discovered by parsing the source file of the current module.
    # "imported-members": False,
    # The directives supporting member documentation also have a exclude-members option that can be used to exclude single member names from documentation, if all members are to be documented.
    "exclude-members": True,
    # autoclass also recognizes the class-doc-from option that can be used to override the global value of autoclass_content.
    # autoclass_content
    # This value selects what content will be inserted into the main body of an autoclass directive. The possible values are:
    # "class" Only the class’ docstring is inserted. This is the default. You can still document __init__ as a separate method using automethod or the members option to autoclass.
    # "both"  Both the class’ and the __init__ method’s docstring are concatenated and inserted.
    # "init"  Only the __init__ method’s docstring is inserted.
    "class-doc-from": "both",
    # The no-value option can be used instead of a blank annotation to show the type hint but not the value:
    "no-value": True,
}
