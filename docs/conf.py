#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# type: ignore

import os
import re
import sys
from pathlib import Path

# pylint: skip-file

ROOT = Path(__file__).resolve().parent.parent
PY_SRC_DIR = ROOT / "src"

sys.path = [str(PY_SRC_DIR)] + sys.path

VERSION_FILE = PY_SRC_DIR / "basd/utils/basd_version.py"
if not VERSION_FILE.is_file():
    sys.exit("Could not find version information file.")
basd_version_py = VERSION_FILE.read_text(encoding="utf-8")
re_version = r"_version\s=\s\"(\d{4}\.\d{2}\.\d+)\""

m = re.search(re_version, basd_version_py)
if not m:
    sys.exit("Something went wrong while extracting the version information.")
_version = m.group(1)

project = "Battery System Designer"
copyright = (
    "2010 - 2024, Fraunhofer-Gesellschaft zur Foerderung der angewandten "
    "Forschung e.V. All rights reserved. See license section for further "
    "information."
)
author = "Fraunhofer IISB - Battery Systems Group"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.graphviz",
    "sphinx.ext.mathjax",
    "sphinx.ext.inheritance_diagram",
    "sphinxcontrib.programoutput",
    "sphinxcontrib.spelling",
]
templates_path = ["_templates"]
html_logo = "./../src/basd/_static/basd-logo.png"
html_theme = "furo"
html_theme_options: Dict[str, Any] = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/foxBMS/BaSD",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": "https://github.com/foxBMS/BaSD/",
    "source_branch": "master",
}
source_suffix = ".rst"
master_doc = "index"
version = _version
release = _version
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
todo_include_todos = False
pygments_style = "sphinx"
pygments_dark_style = "monokai"
html_static_path = ["_static"]
autodoc_default_options = {
    "member-order": "bysource",
    "exclude-members": "__weakref__",
}
autodoc_default_flags = [
    "members",
    "show-inheritance",
    "private-members",
    "special-members",
]

autodoc_mock_imports = ["casadi"]

spelling_word_list_filename = ["spelling.txt"]


def create_api_sources(app, config):
    sources = sorted(list(PY_SRC_DIR.rglob("**/*.py")))
    out_dir = ROOT / "docs/development/api"
    for i in out_dir.rglob("**/*.rst"):
        i.unlink()
    documented_files = []
    for i in sources:
        if any(substring in str(i) for substring in ["vendor", "main", "init"]):
            continue
        out_file = ".".join(str(i.relative_to(ROOT)).split(os.sep)[1:]).replace(
            ".py", ".rst"
        )
        documented_files.append(out_file)
        basename = Path(out_file).name.split(".")[-2]
        heading = " ".join([i.capitalize() for i in basename.split("_")])
        for i in [("Api", "API"), ("Abc", "ABC")]:
            heading = heading.replace(i[0], i[1])
        with open(out_dir / out_file, "w", encoding="utf-8") as f:
            f.write(f".. _{heading.upper().replace(' ', '_')}:\n\n")
            f.write(f"{len(heading)*'#'}\n")
            f.write(f"{heading}\n")
            f.write(f"{len(heading)*'#'}\n")
            f.write("\n")
            f.write(f".. automodule:: {out_file[:-4]}\n")
            f.write("   :members:\n")
            f.write("   :private-members:\n")
            f.write("   :special-members:\n")

    with open(out_dir / "api.rst", "w", encoding="utf-8") as f:
        f.write("###\n")
        f.write("API\n")
        f.write("###\n")
        f.write("\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 1\n")
        f.write("   :caption: Contents:\n")
        f.write("\n   ")
        f.write("\n   ".join(documented_files))
        f.write("\n")


def setup(app):
    app.connect("config-inited", create_api_sources)
