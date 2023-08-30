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

"""parameter_set provides the ParameterSet class which saves the parameter sets used
in the optimization for 3d battery system layout
"""

from dataclasses import dataclass

import numpy as np

from ..requirements import Requirements
from .basic_sets import BasicParameterSet, Overhead, SlaveUtilization
from .overhead_functions import OverheadFunctions


@dataclass(kw_only=True)
class ParameterSet(BasicParameterSet):  # pylint: disable=too-many-instance-attributes
    """Defines the parameter set for the battery system layout

    :param overhead: specifies the overhead functions which should be used
    """

    overhead: OverheadFunctions
    requirements: Requirements

    def get_maximum_module_voltage(self) -> float:
        """returns the minimum module voltage

        :return: minimum module voltage
        """
        return self.cell.electrics.voltage.maximum * self.module.y * self.module.x

    def get_height(self, bjb: bool = False) -> tuple[float, Overhead]:
        """returns the height of a battery system related to the parameter set

        :raises ValueError: stops if overhead is not set
        :return: return pack height and overhead dictionary
        """
        cell_block_height = self.cell.mechanics.height
        cell_block_height_overhead = self.overhead.cell_block_height(
            self, cell_block_height
        )
        cell_block_height += cell_block_height_overhead
        module_height = cell_block_height
        module_height_overhead = self.overhead.module_height(self, module_height)
        module_height += module_height_overhead
        string_height = module_height * self.string.z
        string_height_overhead = self.overhead.string_height(self, string_height)
        string_height += string_height_overhead
        pack_height = string_height * self.pack.z
        # if bjb should be placed in this direction
        if bjb:
            pack_height_overhead = self.overhead.pack_height(self, pack_height)
        else:
            # consider minimal value for this direction as overhead
            pack_height_overhead = (
                (self.overhead.min_height - pack_height)
                if pack_height < self.overhead.min_height
                else 0
            )
        pack_height += pack_height_overhead
        overhead = Overhead(
            (
                cell_block_height_overhead,
                np.round(100 * cell_block_height_overhead / cell_block_height),
            ),
            (
                module_height_overhead,
                np.round(100 * module_height_overhead / module_height),
            ),
            (
                string_height_overhead,
                np.round(100 * string_height_overhead / string_height),
            ),
            (pack_height_overhead, np.round(100 * pack_height_overhead / pack_height)),
        )
        return pack_height, overhead

    def get_length(self, bjb: bool = False) -> tuple[float, Overhead]:
        """returns the length of a battery system related to the parameter set

        :raises ValueError: stops if overhead is not set
        :return: return pack length and overhead dictionary
        """
        if self.cell_rotation == 1:  # 1 = 90° cell rotation
            cell_length = self.cell.mechanics.width
        else:
            cell_length = self.cell.mechanics.length
        cell_block_length = cell_length * self.cell_block.y
        cell_block_length_overhead = self.overhead.cell_block_length(
            self, cell_block_length
        )
        cell_block_length += cell_block_length_overhead
        module_length = cell_block_length * self.module.y
        module_length_overhead = self.overhead.module_length(self, module_length)
        module_length += module_length_overhead
        string_length = module_length * self.string.y
        string_length_overhead = self.overhead.string_length(self, string_length)
        string_length += string_length_overhead
        pack_length = string_length * self.pack.y
        # if bjb should be placed in this direction
        if bjb:
            pack_length_overhead = self.overhead.pack_length(self, pack_length)
        else:
            # consider minimal value for this direction as overhead
            pack_length_overhead = (
                (self.overhead.min_length - pack_length)
                if pack_length < self.overhead.min_length
                else 0
            )
        pack_length += pack_length_overhead
        overhead = Overhead(
            (
                cell_block_length_overhead,
                np.round(100 * cell_block_length_overhead / cell_block_length),
            ),
            (
                module_length_overhead,
                np.round(100 * module_length_overhead / module_length),
            ),
            (
                string_length_overhead,
                np.round(100 * string_length_overhead / string_length),
            ),
            (pack_length_overhead, np.round(100 * pack_length_overhead / pack_length)),
        )
        return pack_length, overhead

    def get_width(self, bjb: bool = False) -> tuple[float, Overhead]:
        """returns the width of a battery system related to the parameter set

        :raises ValueError: stops if overhead is not set
        :return: return pack width and overhead dictionary
        """
        if self.cell_rotation == 1:  # 1 = 90° cell rotation
            cell_width = self.cell.mechanics.length
        else:
            cell_width = self.cell.mechanics.width
        cell_block_width = cell_width * self.cell_block.x
        cell_block_width_overhead = self.overhead.cell_block_width(
            self, cell_block_width
        )
        cell_block_width += cell_block_width_overhead
        module_width = cell_block_width * self.module.x
        module_width_overhead = self.overhead.module_width(self, module_width)
        module_width += module_width_overhead
        string_width = module_width * self.string.x
        string_width_overhead = self.overhead.string_width(self, string_width)
        string_width += string_width_overhead
        pack_width = string_width * self.pack.x
        # if bjb should be placed in this direction
        if bjb:
            pack_width_overhead = self.overhead.pack_width(self, pack_width)
        else:
            # consider minimal value for this direction as overhead
            pack_width_overhead = (
                (self.overhead.min_width - self.overhead.min_width)
                if pack_width < self.overhead.min_width
                else 0
            )
        pack_width += pack_width_overhead
        overhead = Overhead(
            (
                cell_block_width_overhead,
                np.round(100 * cell_block_width_overhead / cell_block_width),
            ),
            (
                module_width_overhead,
                np.round(100 * module_width_overhead / module_width),
            ),
            (
                string_width_overhead,
                np.round(100 * string_width_overhead / string_width),
            ),
            (pack_width_overhead, np.round(100 * pack_width_overhead / pack_width)),
        )
        return pack_width, overhead

    def get_weight(self) -> tuple[float, Overhead]:
        """returns the weight of a battery system related to the parameter set

        :raises ValueError: stops if overhead is not set
        :return: return pack width and overhead dictionary
        """
        cell_block_weight = (
            self.cell.mechanics.weight * self.cell_block.y * self.cell_block.x
        )
        cell_block_weight_overhead = self.overhead.cell_block_gravimetric(
            self, cell_block_weight
        )
        cell_block_weight += cell_block_weight_overhead
        module_weight = cell_block_weight * self.module.y * self.module.x
        module_weight_overhead = self.overhead.module_gravimetric(self, module_weight)
        module_weight += module_weight_overhead
        string_weight = module_weight * self.string.y * self.string.x * self.string.z
        string_weight_overhead = self.overhead.string_gravimetric(self, string_weight)
        string_weight += string_weight_overhead
        pack_weight = string_weight * self.pack.y * self.pack.x * self.pack.z
        pack_weight_overhead = self.overhead.pack_gravimetric(self, pack_weight)
        pack_weight += pack_weight_overhead
        overhead = Overhead(
            (
                cell_block_weight_overhead,
                np.round(100 * cell_block_weight_overhead / cell_block_weight),
            ),
            (
                module_weight_overhead,
                np.round(100 * module_weight_overhead / module_weight),
            ),
            (
                string_weight_overhead,
                np.round(100 * string_weight_overhead / string_weight),
            ),
            (pack_weight_overhead, np.round(100 * pack_weight_overhead / pack_weight)),
        )
        return pack_weight, overhead

    def get_slave_utilization(self, pins_per_slave: int) -> tuple[int, int]:
        """get_slave_utilization determines the min. and max. utilization of the slaves

        :param pins_per_slave: max. number of pins available on the slave
        :return: min. and max. utilization of the slave
        """
        number_of_cell_blocks = self.module.x * self.module.y
        number_of_slaves = int(np.ceil(number_of_cell_blocks / pins_per_slave))
        # For example with 22 number of cell blocks and 12 pins per slave,
        # the workload of 3 slaves would be 7+7+8, which would give a
        # different number for the min/max workload per slave.
        min_work_load = np.floor(number_of_cell_blocks / number_of_slaves)
        max_work_load = np.ceil(number_of_cell_blocks / number_of_slaves)
        utilization = SlaveUtilization(min_work_load, max_work_load, number_of_slaves)
        return utilization
