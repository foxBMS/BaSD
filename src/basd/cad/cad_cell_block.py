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
"""cad_cell_block is used to create the CAD object of a cell block

classes:
    CellBlock

"""

import logging

import cadquery as cq

from . import cad_base
from .cad_cell import Cell


class CellBlock(cad_base.CADBlock):
    """CellBlock class used to build a cell block out of cells

    :ivar x_pos: x position of the block
    :ivar y_pos: y position of the block
    :ivar z_pos: z position of the block
    :ivar x_dir: number of elements in x direction
    :ivar y_dir: number of elements in y direction
    :ivar offset: row offset definition as lists in a list ,
    :ivar padding: space to next objects in x,y,z direction
    :ivar cell_type: cylindrical or prismatic
    :ivar cell_key: cell identifier
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_dir: int,
        y_dir: int,
        z_dir: int,
        row_offset: tuple[float],
        inner_padding: tuple[float],
        outer_padding: tuple[float],
        cell_type: str,
        cell_dimensions: tuple[float],
        rotate: bool,
    ) -> None:
        """init"""
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
        self.cell_type = cell_type
        self.cell_dimensions = cell_dimensions
        self.cell_class = Cell
        self.rotate = rotate

    @property
    def cell_type(self) -> str:
        """cell_type property"""
        return self._cell_type

    @cell_type.setter
    def cell_type(self, value: str):
        if value not in ("cylindrical", "pouch", "prismatic"):
            raise ValueError(f"{value} is not an allowed cell format")
        self._cell_type = value

    def create_block(self, alternate: bool = False) -> cq.Workplane:
        """create_block builds a cell block object

        :param handle: workplane at which the cell block should be build
        :param alternate: rotate the cell block depending on the cell type to
            enable a series connection

        :return: workplane with the cell block as shape object on the stack
        """

        cell_obj = self.cell_class(
            self.x_pos,
            self.y_pos,
            self.z_pos,
            cell_type=self.cell_type,
            dimensions=self.cell_dimensions,
            rotate=self.rotate,
        )
        cell_shape = cell_obj.create_object(alternate)
        result = self.create_object([cell_shape] * 2)
        result = cad_base.CADBlock.add_box(
            result,
            [
                self.outer_padding.x * 2,
                self.outer_padding.y * 2,
                self.outer_padding.z * 2,
            ],
        )
        block_dimensions = cad_base.CADBlock.get_dimensions(result)
        block_center = cad_base.CADBlock.get_dimensions(result, center=True)
        logging.debug("block dimensions: %s", block_dimensions)
        logging.debug("block center: %s", block_center)
        logging.info("Finish cell block creation")
        return result
