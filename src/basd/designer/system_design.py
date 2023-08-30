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

"""system_design provides the SystemDesign class saving all relevant information of
a battery systems
"""

from ..database.battery_cell import BatteryCell
from .basic_sets import ElectricalProperties, MechanicalProperties
from .cooling import Cooling
from .parameter_set import ParameterSet


class SystemDesign:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """The SystemDesign provides all relevant information about a validated battery
    system
    """

    def __init__(
        self,
        layout: ParameterSet,
        mechanical_properties: MechanicalProperties,
        electrical_properties: ElectricalProperties,
    ):
        """_summary_

        :param layout: specifies the 3d layout of the cells in the system
        :param mechanical_properties: mechanical properties calculated by
            determine_battery_system_configuration and check_upper_bounds
        :param electrical_properties: electrical properties calculated by
            determine_battery_system_configuration and check_upper_bounds
        """
        self.layout: ParameterSet = layout
        self.cooling: Cooling = layout.overhead.cooling
        self.cell: BatteryCell = layout.cell
        man = self.cell.identification.manufacturer
        mod = self.cell.identification.model
        self.layout_name = f"{man}_{mod}"
        self.electrical_properties = electrical_properties
        self.mechanical_properties = mechanical_properties
