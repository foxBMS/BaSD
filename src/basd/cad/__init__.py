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

"""Implements the command line interface to tbe Battery System Designer tool."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import NoReturn

import cadquery as cq
from cadquery import Shape, Workplane, exporters
from cadquery.occ_impl.exporters.utils import toCompound

from ..database import CellDatabase
from .cad_battery_pack import BatteryPack
from .cad_system_definition import (
    CellBlockDefinition,
    CellDimensions,
    ComponentDefinition,
    InnerPadding,
    ModuleDefinition,
    OuterPadding,
    RowOffset,
    default_system_definition,
)


def create_cad(  # pylint: disable=too-many-locals
    report_file: Path,
    database: CellDatabase,
    selection: list[int],
    out: Path = Path(os.getcwd()),
    **kwargs,
) -> None:
    """creates a cad model of a battery system and exports it

    :param report_file: a json file with all the system designs
    :param database: the cell database of basd
    :param selection: the numbers of the system designs in the report for which a
        cad model should be created
    :param out: path in which all the exported files should be saved,
        defaults to Path(os.getcwd())
    """
    with open(report_file, mode="r", encoding="utf-8") as f:
        report = json.load(f)
    for system_index in selection:
        system_layout = report[int(system_index)]
        system_definition = get_system_definition(
            system_layout=system_layout, database=database
        )
        logging.debug(
            "system_definition (pack): %s", system_definition["pack_definition"]
        )
        logging.debug(
            "system_definition (string): %s", system_definition["string_definition"]
        )
        logging.debug(
            "system_definition (module): %s", system_definition["module_definition"]
        )
        logging.debug(
            "system_definition (cell block): %s",
            system_definition["cell_block_definition"],
        )
        pack_obj = BatteryPack(
            string_definition={
                **system_definition["string_definition"].__dict__,
                "module_definition": {
                    **system_definition["module_definition"].__dict__,
                    "cell_block_definition": system_definition[
                        "cell_block_definition"
                    ].__dict__,
                },
            },
            **system_definition["pack_definition"].__dict__,
        )
        result = pack_obj.create_pack()
        export_name = (
            f"System_Nr_{system_index}_{system_layout['Manufacturer']}"
            f"_{system_layout['Model']}"
        )
        if kwargs.get("svg", False):
            svg_file_path = out / (export_name + ".svg")
            cells_in_x_dir = (
                system_definition["pack_definition"].x_dir
                * system_definition["string_definition"].x_dir
                * system_definition["module_definition"].x_dir
                * system_definition["cell_block_definition"].x_dir
            )
            cells_in_y_dir = (
                system_definition["pack_definition"].y_dir
                * system_definition["string_definition"].y_dir
                * system_definition["module_definition"].y_dir
                * system_definition["cell_block_definition"].y_dir
            )
            # width and height has to be set dynamically, otherwise the cells can not
            # be distinguished if the fixed number of pixels is too small
            opt = {
                "width": cells_in_x_dir
                * 10000
                * system_definition["cell_block_definition"].cell_dimensions.x,
                "height": cells_in_y_dir
                * 10000
                * system_definition["cell_block_definition"].cell_dimensions.y,
            }
            exporters.export(result, str(svg_file_path), opt=opt)
        if kwargs.get("step", False):
            step_file_path = out / (export_name + ".step")
            exporters.export(result, str(step_file_path))
        if kwargs.get("stl", False):
            step_file_path = out / (export_name + ".stl")
            exporters.export(result, str(step_file_path))


def get_system_definition(system_layout: dict, database: CellDatabase) -> dict:
    """reads the report file and returns for a specific system design the system
    definition needed for CAD models creation

    :param system_layout: the layout from the selected system design
    :param database: the cell database of basd
    :return: a dictionary with the system definition
    """
    system_definition = default_system_definition.copy()
    system_definition = set_component_definitions(
        system_definition,
        system_layout,
        ["Pack", "String", "Module", "Cell block"],
        [(0, 0), (0, 0), (0, 0), (0, 0)],
        [True, True, False, False],
        [False, True, True, True],
    )
    # set pack padding
    system_definition["pack_definition"].inner_padding.x = 0
    system_definition["pack_definition"].inner_padding.y = 0
    system_definition["pack_definition"].inner_padding.z = 0
    system_definition["pack_definition"].outer_padding.x = system_layout[
        "Overhead width pack (m)"
    ]
    system_definition["pack_definition"].outer_padding.y = system_layout[
        "Overhead length pack (m)"
    ]
    system_definition["pack_definition"].outer_padding.z = system_layout[
        "Overhead height pack (m)"
    ]
    # set cell definition
    cell_identifier = f"{system_layout['Manufacturer']}:{system_layout['Model']}"
    cell_obj = database.get(cell_identifier)
    system_definition[
        "cell_block_definition"
    ].cell_dimensions.x = cell_obj.mechanics.width
    system_definition[
        "cell_block_definition"
    ].cell_dimensions.y = cell_obj.mechanics.length
    system_definition[
        "cell_block_definition"
    ].cell_dimensions.z = cell_obj.mechanics.height
    system_definition["cell_block_definition"].cell_type = system_layout["Format"]
    system_definition["cell_block_definition"].rotate = (
        system_layout["Cell orientation"] == "90°"
    )
    return system_definition


def set_component_definitions(  # pylint: disable=too-many-arguments
    system_definition: dict,
    system_layout: dict,
    components: list,
    offsets: list,
    z_dir: list,
    padding: list,
):
    """sets the definition of the passed system components

    :param system_layout: the layout from the selected system design
    :param elements: at which system components the definition should be set
    :param offsets: the offset for the two row representations
    :param z_dir: whether the component has a z-dir or not
    :param padding: whether the padding should be applied or not
    """
    for i, comp in enumerate(components):
        lower_name = comp.lower()
        def_key = lower_name.replace(" ", "_")
        system_definition[f"{def_key}_definition"].y_dir = system_layout[
            f"{comp} y-dir"
        ]
        system_definition[f"{def_key}_definition"].x_dir = system_layout[
            f"{comp} x-dir"
        ]
        if z_dir[i]:
            system_definition[f"{def_key}_definition"].z_dir = system_layout[
                f"{comp} z-dir"
            ]
        if padding[i]:
            system_definition[f"{def_key}_definition"].inner_padding.x = system_layout[
                f"Overhead width {lower_name} (m)"
            ] / (system_layout[f"{comp} x-dir"] + 1)
            system_definition[f"{def_key}_definition"].outer_padding.x = system_layout[
                f"Overhead width {lower_name} (m)"
            ] / (system_layout[f"{comp} x-dir"] + 1)
            system_definition[f"{def_key}_definition"].inner_padding.y = system_layout[
                f"Overhead length {lower_name} (m)"
            ] / (system_layout[f"{comp} y-dir"] + 1)
            system_definition[f"{def_key}_definition"].outer_padding.y = system_layout[
                f"Overhead length {lower_name} (m)"
            ] / (system_layout[f"{comp} y-dir"] + 1)
            system_definition[f"{def_key}_definition"].inner_padding.z = system_layout[
                f"Overhead height {lower_name} (m)"
            ] / (system_layout.get(f"{comp} z-dir", 1) + 1)
            system_definition[f"{def_key}_definition"].outer_padding.z = system_layout[
                f"Overhead height {lower_name} (m)"
            ] / (system_layout.get(f"{comp} z-dir", 1) + 1)
        system_definition[f"{def_key}_definition"].row_offset.first = offsets[i][0]
        system_definition[f"{def_key}_definition"].row_offset.second = offsets[i][1]
    return system_definition
