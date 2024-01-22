#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 - 2024, Fraunhofer-Gesellschaft zur Foerderung der angewandten Forschung e.V.
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

"""cad_battery_module is used to create a CAD object of a battery module"""

import logging

import cadquery as cq

from . import cad_base
from .cad_cell_block import CellBlock


class BatteryModule(cad_base.CADBlock):
    """BatteryModule class used to build a module out of cell blocks

    :ivar x_pos: x position of the block
    :ivar y_pos: y position of the block
    :ivar z_pos: z position of the block
    :ivar x_dir: number of elements in x direction
    :ivar y_dir: number of elements in y direction
    :ivar offset: row offset definition as lists in a list ,
    :ivar padding: space to next objects in x,y,z direction
    :ivar block_definition: a dictionary with the cell block definition
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_dir: int,
        y_dir: int,
        z_dir: int,
        row_offset: list[float],
        inner_padding: tuple[float],
        outer_padding: tuple[float],
        cell_block_definition: dict,
        alternate=True,
    ):  # pylint: disable=R0801
        super().__init__(
            x_pos,
            y_pos,
            z_pos,
            x_dir,
            y_dir,
            1,
            row_offset,
            inner_padding,
            outer_padding,
        )
        self.cell_block_definition = cell_block_definition
        self.alternate = alternate

    def create_module(self) -> cq.Workplane:
        """create_module builds a module object

        :param handle: workplane at which the module should be build

        :return: workplane with the module as shape object on the stack
        """
        cell_block_obj = CellBlock(
            **self.cell_block_definition,
        )
        # handle_cell_block = cq.Workplane()
        block_shape = cell_block_obj.create_block()
        # handle_alternated_cell_block = cq.Workplane()
        block_shape_rotated = cell_block_obj.create_block(True)
        # for series connection, the cell block are rotated alternately in the module
        component_list = [block_shape, block_shape_rotated]
        result = self.create_object(component_list, self.alternate)
        result = cad_base.CADBlock.add_box(  # pylint: disable=duplicate-code
            result,
            [
                self.outer_padding.x * 2,
                self.outer_padding.y * 2,
                self.outer_padding.z * 2,
            ],
        )
        module_dimensions = cad_base.CADBlock.get_dimensions(result)
        module_center = cad_base.CADBlock.get_dimensions(result, center=True)
        logging.debug("module dimensions: %s", module_dimensions)
        logging.debug("module center: %s", module_center)
        logging.info("Finish module creation")
        return result
