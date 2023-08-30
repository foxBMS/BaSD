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

"""overhead functions defines for each element in the battery system the expected
overhead caused by busbar, casing, etc.
"""

from .basic_sets import BasicParameterSet
from .cooling import Cooling
from .overhead_functions_abc import AbcOverheadFunctions


class OverheadFunctions(AbcOverheadFunctions):
    """OverheadFunctions class determines the overhead for each battery system
    layout

    :param cooling: the cooling type used in the system
    :param cooling_width: the extra width due to the cooling system
    :param cooling_length: the extra length due to the cooling system
    :param cooling_height: the extra height due to the cooling system
    :param cooling_weight: the extra weight due to the cooling system

    :cvar min_length: minimal length of the battery system
    :cvar min_width: minimal width of the battery system
    :cvar min_height: minimal height of the battery system

    """

    min_height: float = 0.1
    min_length: float = 0.1
    min_width: float = 0.1

    # pylint: disable=R0801
    def __init__(self, cooling: Cooling):
        self.cooling: Cooling = cooling
        self.cooling_width: float
        self.cooling_length: float
        self.cooling_height: float
        self.cooling_weight: float

        if cooling == Cooling.AIR:
            self.cooling_width = 0.2
            self.cooling_length = 0.2
            self.cooling_height = 0.0
            self.cooling_weight = 0.1
        elif cooling == Cooling.GLYCOL:
            self.cooling_width = 0.07
            self.cooling_length = 0.07
            self.cooling_height = 0.0
            self.cooling_weight = 0.25
        elif cooling == Cooling.REFRIGERANT:
            self.cooling_width = 0.03
            self.cooling_length = 0.03
            self.cooling_height = 0.0
            self.cooling_weight = 0.2

    def pack_height(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_height: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the pack height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of strings

        :return: overhead

        """
        if (
            layout.requirements.cont_max_charge_power
            > layout.requirements.cont_max_discharge_power
        ):
            max_power = layout.requirements.cont_max_charge_power
        else:
            max_power = layout.requirements.cont_max_discharge_power
        return 0.10 + max((0, (max_power - 1e5) * 0.0003))

    def pack_length(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_length: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the pack length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of strings

        :return: overhead

        """
        if (
            layout.requirements.cont_max_charge_power
            > layout.requirements.cont_max_discharge_power
        ):
            max_power = layout.requirements.cont_max_charge_power
        else:
            max_power = layout.requirements.cont_max_discharge_power
        return 0.10 + max((0, (max_power - 1e5) * 0.0005))

    def pack_width(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_width: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the pack width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of strings

        :return: overhead

        """
        if (
            layout.requirements.cont_max_charge_power
            > layout.requirements.cont_max_discharge_power
        ):
            max_power = layout.requirements.cont_max_charge_power
        else:
            max_power = layout.requirements.cont_max_discharge_power
        return 0.10 + max((0, (max_power - 1e5) * 0.0008))

    def string_height(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_height: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the string height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of modules

        :return: overhead

        """
        return 0.02

    def string_length(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_length: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the string length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of modules

        :return: overhead

        """
        return 0.03

    def string_width(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_width: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the string width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of modules

        :return: overhead

        """
        return 0.05

    def module_height(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_height: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the module height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of cell blocks

        :return: overhead

        """
        return 0.025

    def module_length(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_length: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the module length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of cell blocks

        :return: overhead

        """
        if layout.cell_rotation == 1:
            return 0.019
        return 0.029

    def module_width(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_width: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the module width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of cell blocks

        :return: overhead

        """
        if layout.cell_rotation == 1:
            return 0.029
        return 0.019

    def cell_block_height(self, layout: BasicParameterSet, base_height: float) -> float:
        """overhead for the cell block height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of cells

        :return: overhead

        """
        if layout.cell.mechanics.format == "prismatic":
            overhead_percentage = OverheadFunctions.linear(
                layout.cell_block.y * layout.cell_block.x, 0.24, 2
            )
        if layout.cell.mechanics.format == "cylindrical":
            overhead_percentage = 1
        if layout.cell.mechanics.format == "pouch":
            overhead_percentage = OverheadFunctions.linear(layout.cell_block.y, 0.09, 3)
        return base_height * (overhead_percentage / 100 + self.cooling_height)

    def cell_block_length(self, layout: BasicParameterSet, base_length: float) -> float:
        """overhead for the cell block length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of cells

        :return: overhead

        """
        if layout.cell.mechanics.format == "prismatic":
            if layout.cell_block.y > 1 and layout.cell_rotation == 1:
                overhead_percentage = 10000000
            else:
                overhead_percentage = OverheadFunctions.sigmoid(
                    layout.cell_block.y, 2, 8.37, 3, 2
                )
        if layout.cell.mechanics.format == "cylindrical":
            overhead_percentage = OverheadFunctions.sigmoid(
                layout.cell_block.y, 2.26, 9.82, 4, 3
            )
        if layout.cell.mechanics.format == "pouch":
            if layout.cell_block.y > 1 and layout.cell_rotation == 1:
                overhead_percentage = 10000000
            else:
                overhead_percentage = OverheadFunctions.sigmoid(
                    layout.cell_block.y, 2.29, 9.98, 5, 4
                )
        return base_length * (overhead_percentage / 100 + self.cooling_length)

    def cell_block_width(self, layout: BasicParameterSet, base_width: float) -> float:
        """overhead for the cell block width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of cells

        :return: overhead

        """
        if layout.cell.mechanics.format == "prismatic":
            if layout.cell_block.x > 1 and layout.cell_rotation == 0:
                overhead_percentage = 10000000
            else:
                overhead_percentage = OverheadFunctions.sigmoid(
                    layout.cell_block.x, 2, 8.25, 3, 2
                )
        if layout.cell.mechanics.format == "cylindrical":
            overhead_percentage = OverheadFunctions.sigmoid(
                layout.cell_block.x, 2.26, 9.82, 4, 3
            )
        if layout.cell.mechanics.format == "pouch":
            if layout.cell_block.x > 1 and layout.cell_rotation == 0:
                overhead_percentage = 10000000
            else:
                overhead_percentage = 5
        return base_width * (overhead_percentage / 100 + self.cooling_width)

    def pack_gravimetric(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_weight: float,  # pylint: disable=unused-argument
    ) -> float:
        """gravimetric overhead for the pack

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of strings

        :return: overhead
        """
        return 4.24

    def string_gravimetric(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_weight: float,  # pylint: disable=unused-argument
    ) -> float:
        """gravimetric overhead for the string

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of modules

        :return: overhead
        """
        return 0.57

    def module_gravimetric(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_weight: float,  # pylint: disable=unused-argument
    ) -> float:
        """gravimetric overhead for the module

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of cell blocks

        :return: overhead
        """
        return 0.29

    def cell_block_gravimetric(
        self, layout: BasicParameterSet, base_weight: float
    ) -> float:
        """gravimetric overhead for the cell blocks

        :param layout: layout parameter
        :param base_block_weight: absolute weight caused by the number of cells

        :return: overhead
        """
        if layout.cell.mechanics.format == "prismatic":
            overhead_percentage = OverheadFunctions.linear(
                layout.cell_block.y * layout.cell_block.x, 0.21, 6.36
            )
        if layout.cell.mechanics.format == "cylindrical":
            overhead_percentage = OverheadFunctions.sigmoid(
                layout.cell_block.y * layout.cell_block.x, 3.8, 17.9, 27, 23
            )
        if layout.cell.mechanics.format == "pouch":
            overhead_percentage = OverheadFunctions.sigmoid(
                layout.cell_block.y * layout.cell_block.x, 3.6, 15.3, 24, 12
            )
        return base_weight * (overhead_percentage / 100 + self.cooling_weight)
