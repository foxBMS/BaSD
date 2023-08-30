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
"""cad_battery_pack is used to create the CAD object of a battery pack

classes:
    BatteryPack

"""
import logging

import cadquery as cq

from . import cad_base
from .cad_battery_string import BatteryString


class BatteryPack(cad_base.CADBlock):
    """BatteryPack class used to build pack out of battery strings

    :ivar x_pos: x position of the block
    :ivar y_pos: y position of the block
    :ivar z_pos: z position of the block
    :ivar x_dir: number of elements in x direction
    :ivar y_dir: number of elements in y direction
    :ivar z_dir: number of elements in z direction
    :ivar offset: row offset definition as lists in a list ,
    :ivar padding: space to next objects in x,y,z direction
    :ivar string_definition: a dictionary with the string definition
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
        string_definition: dict,
    ):  # pylint: disable=R0801
        super().__init__(
            x_pos,
            y_pos,
            z_pos,
            x_dir,
            y_dir,
            z_dir,
            row_offset,
            inner_padding,
            outer_padding,
        )
        self.string_definition = string_definition

    def create_pack(self) -> cq.Workplane:
        """create_pack builds a battery pack object

        :param handle: workplane at which the string should be build

        :return: workplane with the string as shape object on the stack
        """

        string_obj = BatteryString(**self.string_definition)
        string_shape = string_obj.create_string()
        result = self.create_object([string_shape] * 2)
        result = cad_base.CADBlock.add_box(
            result,
            add=[self.outer_padding.x, self.outer_padding.y, self.outer_padding.z],
        )
        pack_dimensions = cad_base.CADBlock.get_dimensions(result)
        pack_center = cad_base.CADBlock.get_dimensions(result, center=True)
        logging.debug("pack dimensions: %s", pack_dimensions)
        logging.debug("pack center: %s", pack_center)
        logging.info("Finish Pack creation")
        return result
