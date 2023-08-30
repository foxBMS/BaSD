#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 - 2023, Fraunhofer-Gesellschaft zur Foerderung der angewandten Forschung e.V.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Utility functions"""
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft7Validator, RefResolver
from jsonschema.exceptions import ValidationError
from platformdirs import user_data_dir

IS_SPHINX_BUILD = f"{os.sep}sphinx" in sys.argv[0]

if IS_SPHINX_BUILD:
    #: top level directory of BaSD to store application specific settings
    BASD_DIR = Path(os.path.join("$user_data_dir", "basd", "fhg-iisb")).as_posix()
    #: temporary directory of BaSD
    BASD_TMP_DIR = Path(Path(BASD_DIR) / "tmp").as_posix()
    #: logging directory of BaSD
    BASD_LOG_DIR = Path(Path(BASD_DIR) / "log").as_posix()
    #: store the user's batter cell database
    BASD_DATABASE_DIR = Path(Path(BASD_DIR) / "db").as_posix()
    #: module relative path to the json schemas that are used to validate the database
    DB_SCHEMA_PATH = (
        Path("$install_path").parent / "database" / "db_schema" / "db.schema.json"
    ).as_posix()

else:
    BASD_DIR = Path(user_data_dir("basd", "fhg-iisb"))
    #: temporary directory of BaSD
    BASD_TMP_DIR = Path(BASD_DIR / "tmp")
    #: logging directory of BaSD
    BASD_LOG_DIR = Path(BASD_DIR / "log")
    #: store the user's batter cell database
    BASD_DATABASE_DIR = Path(BASD_DIR / "db")
    #: module relative path to the json schemas that are used to validate the database
    DB_SCHEMA_PATH = (
        Path(__file__).parent.parent / "database" / "db_schema" / "db.schema.json"
    )

USE_HELP = "Use '--help' to get usage information."
ERROR_MESSAGES = {
    "no-database": "A database directory or file must be provided.",
    "no-requirements": "A system requirements file must be provided.",
    "no-report": "A report output file or directory must be provided.",
}
for k, v in ERROR_MESSAGES.items():
    ERROR_MESSAGES[k] = f"{v}\n{USE_HELP}"


def ensure_app_directories() -> None:
    """Create application directories if they do not exist."""
    for i in [BASD_DIR, BASD_TMP_DIR, BASD_LOG_DIR, BASD_DATABASE_DIR]:
        if not i.exists():
            i.mkdir(parents=True, exist_ok=True)
        else:
            if "-vv" in sys.argv:
                print(f"DEBUG:root:App directory '{i}' already exists.")


if not IS_SPHINX_BUILD:
    ensure_app_directories()


def validate_json_file(json_file: Path) -> dict:
    """Returns the content of a json file as dict, if it is a valid json file.

    :param json_file: json file to be read

    :return: the data loaded from the read json file or an empty dict in case the json
             file was invalid.
    """
    resulting_dict = {}
    try:
        resulting_dict = json.loads(json_file.read_text(encoding="utf-8"))
    except json.decoder.JSONDecodeError:
        logging.warning(f"{json_file} is not a valid json file and will be ignored.")
    return resulting_dict


def validate_dict_against_db_schema(cfg: dict) -> tuple[bool, str]:
    """Checks that a dictionary matches a defined schema.

    :param cfg: dictionary which should match a certain json schema

    :return: True if the dictionary matches the schema otherwise False
    """
    err_msg = ""
    validator_version = Draft7Validator
    with open(DB_SCHEMA_PATH, mode="r", encoding="utf-8") as f:
        schema = json.load(f)
    if sys.platform.lower().startswith("win32"):
        uri_template = "file:///{0}"
    else:
        uri_template = "file:{0}"
    base_uri = uri_template.format(str(DB_SCHEMA_PATH.absolute().as_posix()))
    validator_version.check_schema(schema)
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    validator = validator_version(schema, resolver=resolver, format_checker=None)
    try:
        validator.validate(cfg)
    except ValidationError as err:
        err_msg = str(err)
        logging.error(err_msg)
        return False, str(err_msg)
    return True, err_msg


def get_iso_date_today() -> str:
    """returns the date string for the output

    :return: current date in ISO format.
    """
    today = datetime.today()
    return today.strftime("%Y-%m-%d")


def set_logging_level(verbosity: int = 0) -> None:
    """sets the module logging level

    :param verbosity: verbosity level"""
    logging_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    logging.basicConfig(
        level=logging_levels[min(verbosity, max(logging_levels.keys()))]
    )


def get_program_config() -> dict:
    """Returns the installation directories of the program

    :return: relevant program directories"""
    program_config = {
        "installation path": BASD_DIR,
        "temporary directory": BASD_TMP_DIR,
        "logging directory": BASD_LOG_DIR,
        "user database directory": BASD_DATABASE_DIR,
        "database validation configuration": DB_SCHEMA_PATH,
    }
    return program_config
