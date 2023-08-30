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

"""cell database definition"""

import json
import logging
import shutil
import sys
import xml.etree.ElementTree as et
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import numpy as np
from scipy.interpolate import interp1d

from ..utils import (
    BASD_DATABASE_DIR,
    BASD_LOG_DIR,
    validate_dict_against_db_schema,
    validate_json_file,
)
from .battery_cell import BatteryCell


class CellNotFoundInDatabase(Exception):
    """Exception to throw when a cell is not found in the database"""


class CellDatabase:
    """CellDatabase class

    :ivar cells: all cells in the database as BatteryCell object
    :ivar identifiers: the identifiers of all used cells
    :ivar db_cell_file_relation: the file name to each cell identifier
    :ivar index: actual index used if the database is used as iterator

    """

    def __init__(self, database_dir: Path = BASD_DATABASE_DIR) -> None:
        """constructor of the CellDatabase class

        :param database_dir: path to used cell database, defaults to BASD_DATABASE_DIR
        """
        cells, nr_errors, db_cell_file_relation = CellDatabase.validate_database(
            database_dir
        )
        if nr_errors:
            logging.error(
                "Error in validation step. Cell database could not be initialized"
            )
            sys.exit(nr_errors)
        if not cells:
            logging.warning("Cell database is empty")
        self.cells: list[BatteryCell] = [BatteryCell(i) for i in cells]
        self.identifiers = [str(x) for x in self.cells]
        self.db_cell_file_relation = db_cell_file_relation
        self._index: int = -1

    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> BatteryCell:
        self._index += 1
        if self._index >= len(self.cells):
            self._index = -1
            raise StopIteration
        return self.cells[self._index]

    def __reversed__(self) -> list:
        return self.cells[::-1]

    def add(  # pylint: disable=too-many-locals,too-many-branches
        self, to_be_added: list[Path], mapping: Optional[Path], update_existing=False
    ) -> int:
        """add a list of battery cell to the cell database

        :param to_be_added: list of json or xml file containing the cell data
        :param mapping: json file with the relation between a xml file and the used
            json format
        :param update_existing: whether an already existing cell in the database should
            be updated, defaults to False
        :return: error code
        """
        all_files = []
        for i in to_be_added:
            i = Path(i)
            if i.is_file():
                all_files.append(i)
            else:
                all_files.extend(
                    Path(p)
                    for p in i.rglob("**/*")
                    if p.is_file() and (p.suffix in (".json", ".xml"))
                )
        # now we have all json and xml database files
        install_to_database = []
        for i in all_files:
            if i.suffix == ".xml":
                if mapping is None:
                    logging.warning(
                        "%s can not be added, because a mapping is not provided", i
                    )
                    continue
                i = self._battery_pass_to_basd(i, Path(mapping))
                install_to_database.append(i)
            else:
                install_to_database.append(i)
        # now we have all files in json format, let's validate them, and if they pass, add
        # them to the database
        err = 0
        for i in install_to_database:
            with open(i, encoding="utf-8") as f:
                data = json.load(f)
            if validate_dict_against_db_schema(data)[0]:
                if update_existing:
                    shutil.copy(i, BASD_DATABASE_DIR)
                else:
                    if Path(BASD_DATABASE_DIR / i.name).exists():
                        logging.error(f"Cannot add {i} as the file already exists.")
                    else:
                        shutil.copy(i, BASD_DATABASE_DIR)
            else:
                err += 1
        return err

    def get(self, cell_identifier: str) -> BatteryCell:
        """get returns the BatteryCell object specified by the identifier

        :param cell_identifiers: specifies the cell
        :return: the BatteryCell object
        """
        try:
            i = self.identifiers.index(cell_identifier)
            return self.cells[i]
        except ValueError as not_existing:
            raise CellNotFoundInDatabase(
                f"'{cell_identifier}' does not exist in the database."
            ) from not_existing

    def remove(self, cell_identifiers: list[str]) -> int:
        """removes specified cells from the cell database

        :param cell_identifiers: specified cells to remove
        :return: error code
        """
        for cell_identifier in cell_identifiers:
            self.db_cell_file_relation[cell_identifier].unlink()
        return 0

    def list_cells(self) -> int:
        """lists all cells in the cell database
        :return: error code
        """
        if len(self.cells) == 0:
            print("Cell database is empty", file=sys.stderr)
            return 1
        for cell in self.cells:
            print(cell)
        return 0

    def show(self, cell_identifiers: list[str]) -> int:
        """show the data of a specified battery cell in the database

        :param cell_identifiers: a list of cell identifiers
        :return: error code
        """
        err = 0
        for cell_identifier in cell_identifiers:
            try:
                cell_obj = self.get(cell_identifier)
                print(f"Cell: {cell_identifier}")
                print(repr(cell_obj))
            except CellNotFoundInDatabase:
                print(f"cell '{cell_identifier}' not found", file=sys.stderr)
                err += 1
        return err

    def _battery_pass_to_basd(self, battery_pass: Path, mapping: Path) -> Path:
        """converts the xml file from the battery pass to a json file used in basd

        :param battery_pass: xml file of the battery pass
        :param mapping: the relation between json and xml file
        :return: path to the new generated json
        """
        tree = et.parse(battery_pass)
        root = tree.getroot()
        with open(mapping, mode="r", encoding="utf-8") as f:
            mapping_json = json.load(f)
        cell_data = self._loop_json(mapping_json, root, battery_pass)
        path_to_json = battery_pass.parent / (battery_pass.stem + ".json")
        with open(path_to_json, mode="w", encoding="utf-8") as f:
            json.dump(cell_data, f, indent=4)
        return path_to_json

    def _loop_json(  # pylint: disable=too-many-branches
        self, mapping_json: dict, xml_root: et.Element, battery_pass: Path
    ) -> dict[str, Union[str, float]]:
        """loops recursively over the mapping file and adds cell data from
        battery pass xml file

        :param mapping_json: mapping between cell description in xml and json
        :param xml_root: root of the xml tree
        :param battery_pass: path to xml file
        :return: cell data in json format
        """
        # function to iterate recursive over the mapping dictionary
        # create copy to change key and values without throwing exception
        new_json = mapping_json.copy()
        for key, value in mapping_json.items():
            uppercase = False
            # if key is xPath
            if "/" in key:
                new_key = CellDatabase._xml_find(key, xml_root, battery_pass)
                new_json[new_key] = new_json.pop(key)
                key = new_key
            elif "discharge curve" in key:
                new_json[key] = CellDatabase._mapping_handle_discharge_curve(
                    value, xml_root, battery_pass
                )
                continue
            # the loop_json function is used in a recursive manner
            if isinstance(value, dict):
                new_json[key] = self._loop_json(value, xml_root, battery_pass)
            elif isinstance(value, str):
                if "uppercase:" in value:
                    uppercase = True
                    value = value.replace("uppercase:", "")
                # evaluate formulas in the mapping json
                if " * " in value or " / " in value:
                    list_of_exp = value.split(" ")
                    exp_copy = list_of_exp.copy()
                    # replace xml paths with the corresponding values
                    for i, exp_part in enumerate(list_of_exp):
                        if "/" in exp_part and exp_part != "/":
                            exp_copy[i] = CellDatabase._xml_find(
                                exp_part, xml_root, battery_pass
                            )
                    exp_copy = " ".join(exp_copy)
                    # execute expression evaluation
                    new_json[key] = CellDatabase._evaluation(exp_copy)
                # if value is only a xml path then replace xml path with corresponding
                # value
                elif "/" in value:
                    xml_value = CellDatabase._xml_find(value, xml_root, battery_pass)
                    try:
                        new_json[key] = float(xml_value)
                    except ValueError:
                        if uppercase:
                            new_json[key] = xml_value[0].upper() + xml_value[1:]
                        else:
                            new_json[key] = xml_value
        return new_json

    @staticmethod
    def remove_db() -> int:
        """remove_db deletes all data/files in the database"""
        shutil.rmtree(BASD_DATABASE_DIR)
        BASD_DATABASE_DIR.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def validate_database(database: Path) -> tuple[list, int, dict[str, str]]:
        """Validates the database files and returns a list of successfully read cells

        :param database: path to the desired battery cell database
        :return: a tuple with a list of all validated cells, the validation error count
            and the file to cell identifier dictionary
        """
        if database.is_dir():
            configs = list(database.glob("**/*.json"))
        else:
            configs = [database]
        cells = []
        database_validation_errors = 0
        file_cell_relation = {}
        for i in configs:
            cfg = validate_json_file(i)
            # check schema specified in db_schema folder
            if cfg:
                passes_schema, err_msg = validate_dict_against_db_schema(cfg)
                if passes_schema:
                    manufacturer = cfg["identification"]["manufacturer"]
                    model = cfg["identification"]["model"]
                    identifier = f"{manufacturer}:{model}"
                    logging.debug(
                        "Adding configuration read form %s to cell list...", identifier
                    )
                    file_cell_relation[identifier] = i
                    cells.append(cfg)
                else:
                    # write error message into log files
                    database_validation_errors += 1
                    logfile_name = (
                        datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
                        + f"_{i.stem}.txt"
                    )
                    logfile = Path(BASD_LOG_DIR / logfile_name)
                    logging.warning(
                        f"The database schema does not apply to {i.absolute().resolve()} and "
                        f"therefore it will not be added to the database "
                        f"(for details see the at {logfile})."
                    )
                    err_msg = f"In {i}:{err_msg}"
                    logfile.write_text(err_msg, encoding="utf-8")
            else:
                database_validation_errors += 1
                logging.warning(
                    f"{i.absolute()} is not a valid json file and will therefore not be "
                    "added to the database."
                )
        return (cells, database_validation_errors, file_cell_relation)

    @staticmethod
    def _mapping_handle_discharge_curve(
        value: str, xml_root: et.ElementTree, battery_pass: Path
    ) -> list[float]:
        """handles the mapping of the discharge curve

        :param value: xml path where the voltage data points are
        :param xml_root: root element of the xml tree
        :param battery_pass: path to the xml file
        :return: list of the new discharge curve voltage values
        """
        reverse = False
        # if the data points in the xml file corresponds to a charge curve
        if "reverse:" in value:
            reverse = True
            value = value.replace("reverse:", "")
        voltages = CellDatabase._xml_find(value, xml_root, battery_pass)
        # handle empty strings in the xml file
        float_strings = voltages.replace(" ", "").split(",")
        voltages = []
        # only consider values that can be converted to a float
        for float_string in float_strings:
            try:
                voltages.append(float(float_string))
            except ValueError:
                continue
        # resample the discharge curve in a way that a list with 100 voltage values
        # is created
        number_of_voltages = len(voltages)
        x_old = np.linspace(0, 100, number_of_voltages, endpoint=True)
        interpolation = interp1d(x_old, voltages)
        x_new = np.arange(0, 101)
        voltages = interpolation(x_new)
        if reverse:
            return list(voltages)[::-1]
        return list(voltages)

    @staticmethod
    def _evaluation(expression: str) -> float:
        """evaluations a passed expression containing only multiplication and division

        :param expression: the expression
        :return: the calculated value
        """
        factors = expression.split("*")
        result = 1.0
        for factor in factors:
            if "/" not in factor:
                result *= float(factor)
            else:
                factor_split = factor.split("/")
                devisors = factor_split[1]
                factor = factor_split[0]
                result *= float(factor) / float(devisors)
        return result

    @staticmethod
    def _xml_find(key: str, root: et.Element, source: Path) -> str:
        """returns the value of a xml element specified by a key

        :param key: the key to specify the xml element
        :param root: the root of the xml tree
        :param source: path of the xml file
        :return: value in the xml tree
        """
        try:
            return root.find(key).text.strip()
        except AttributeError:
            logging.error("Key: %s could not be found in %s", key, source.name)
            sys.exit(1)
