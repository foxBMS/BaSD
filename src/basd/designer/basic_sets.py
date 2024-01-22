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

"""Basic classes of the used parameter sets"""

from dataclasses import dataclass, field
from typing import Literal

from ..database.battery_cell import BatteryCell


@dataclass
class CellBlock:
    """dataclass for the cell block

    :param x: number of cells in x-direction
    :param y: number of cells in y-direction
    """

    x: int = 1
    y: int = 1


@dataclass
class Module:
    """dataclass for the module

    :param x: number of cell blocks in x-direction
    :param y: number of cell blocks in y-direction

    """

    x: int = 1
    y: int = 1


@dataclass
class String:
    """dataclass for the string

    :param x: number of modules in x-direction
    :param y: number of modules in y-direction
    :param z: number of modules in z-direction

    """

    x: int = 1
    y: int = 1
    z: int = 1


@dataclass
class Pack:
    """dataclass for the pack

    :param x: number of strings in x-direction
    :param y: number of strings in y-direction
    :param z: number of strings in z-direction

    """

    x: int = 1
    y: int = 1
    z: int = 1


@dataclass
class Overhead:
    """dataclass for the overhead values

    :param cell_block: overhead value in a specific direction
    :param module: overhead value in a specific direction
    :param string: overhead value in a specific direction
    :param pack: overhead value in a specific direction

    """

    cell_block: tuple[float, int]
    module: tuple[float, int]
    string: tuple[float, int]
    pack: tuple[float, int]


@dataclass
class SlaveUtilization:
    """SlaveUtilization dataclass

    :param min: minimal workload of the slaves
    :param max: maximal workload of the slaves
    :param slaves: number of slaves per modules
    """

    min: int
    max: int
    slaves: int


@dataclass
class ElectricalConfiguration:  # pylint: disable=too-many-instance-attributes
    """dataclass to save the electrical configuration of a battery system

    :param cells_in_parallel: number of cells connected in parallel
    :param cells_in_series: number of cells connected in series
    :param nominal_system_voltage: the nominal battery system voltage
    :param system_capacity: the battery system capacity
    :param lower_bound_cell_voltage: the minimal cell voltage in the configuration
    :param upper_bound_cell_voltage: the maximal cell voltage in the configuration
    :param used_cell_capacity: the usable cell capacity in the configuration
    :param system_energy: the energy of the battery system

    """

    cells_in_parallel: int
    cells_in_series: int
    nominal_system_voltage: float
    system_capacity: float
    lower_bound_cell_voltage: float
    upper_bound_cell_voltage: float
    used_cell_capacity: float
    system_energy: float


@dataclass
class MechanicalProperties:  # pylint: disable=too-many-instance-attributes
    """dataclass for the mechanical properties of a system

    :param height: the height of the system in meter
    :param length: the length of the system in meter
    :param width: the width of the system in meter
    :param weight: the weight of the system in meter
    :param height_overhead: the height overhead of the system in meter
    :param length_overhead: the length overhead of the system in meter
    :param width_overhead: the width overhead of the system in meter
    :param weight_overhead: the weight overhead of the system in meter

    """

    height: float
    length: float
    width: float
    weight: float
    height_overhead: float
    length_overhead: float
    width_overhead: float
    weight_overhead: float
    height_without_overhead: float
    length_without_overhead: float
    width_without_overhead: float
    weight_without_overhead: float
    volume: float = None

    def __post_init__(self) -> None:
        """set the value for the volume"""
        if self.volume is None:
            self.volume = self.height * self.length * self.width


@dataclass(kw_only=True)
class BasicParameterSet:  # pylint: disable=too-many-instance-attributes
    """Defines the basic parameter set for the battery system layout

    :param cell: used cell for the parameter set
    :param cell_block: cell block related parameter
    :param module: module related parameter
    :param string: string related parameter
    :param pack: pack related parameter
    :param cell_rotation: specifies the rotation of the cell in the layout
    """

    cell: BatteryCell
    cell_block: CellBlock = field(default_factory=CellBlock)
    module: Module = field(default_factory=Module)
    string: String = field(default_factory=String)
    pack: Pack = field(default_factory=Pack)
    cell_rotation: int = 0

    def __getitem__(
        self, item: Literal["series", "parallel"]
    ) -> tuple[Module, String] | tuple[CellBlock, Pack]:
        """layout parameters related to series and parallel connection
        are accessed by the key 'series' or 'parallel'.

        :param item : used to access specific series or parallel related elements

        """
        if item == "series":  # returns series connection related layout parameter
            return (self.module, self.string)
        if item == "parallel":  # returns parallel connection related layout parameter
            return (self.cell_block, self.pack)
        raise KeyError(
            f"Only 'series', 'parallel' and integer are allowed as keys, but {item} is not"
        )

    def __setitem__(self, item: str, value: list) -> None:
        """__getitem__ layout parameters related to series and parallel connection
        are set by the key 'series' or 'parallel'.

        :param item: used to set specific series or parallel related elements

        """
        if item == "series":
            # sets series connection related layout parameter
            self.module = Module(value[0], value[1])
            self.string = String(value[2], value[3], value[4])
        elif item == "parallel":
            # sets parallel connection related layout parameter
            self.cell_block = CellBlock(value[0], value[1])
            self.pack = Pack(value[2], value[3], value[4])
        else:
            raise KeyError(
                f"Only 'series', 'parallel' and integer are allowed as keys, but {item} is not"
            )


@dataclass
class ElectricalProperties:  # pylint: disable=too-many-instance-attributes
    """the dataclass for the electrical properties of a system

    :param module_voltage: the voltage of the modules in the system
    """

    def __init__(
        self,
        parameter_set: BasicParameterSet,
        electrical_configuration: ElectricalConfiguration,
        **kwargs,
    ):
        """Constructor of ElectricalProperties"""
        self.max_module_voltage = kwargs.get(
            "maximum module voltage",
            parameter_set.cell.electrics.voltage.maximum
            * parameter_set.module.y
            * parameter_set.module.x,
        )
        self.min_module_voltage = (
            parameter_set.cell.electrics.voltage.minimum
            * parameter_set.module.y
            * parameter_set.module.x
        )
        self.nom_module_voltage = (
            parameter_set.cell.electrics.voltage.nominal
            * parameter_set.module.y
            * parameter_set.module.x
        )
        self.cells_in_parallel = (
            parameter_set.cell_block.x
            * parameter_set.cell_block.y
            * parameter_set.pack.x
            * parameter_set.pack.y
            * parameter_set.pack.z
        )
        self.cells_in_series = (
            parameter_set.module.x
            * parameter_set.module.y
            * parameter_set.string.x
            * parameter_set.string.y
            * parameter_set.string.z
        )
        self.nominal_system_voltage = (
            parameter_set.cell.electrics.voltage.nominal * self.cells_in_series
        )
        self.system_capacity = (
            electrical_configuration.used_cell_capacity * self.cells_in_parallel
        )
        self.lower_bound_cell_voltage = (
            electrical_configuration.lower_bound_cell_voltage
        )
        self.upper_bound_cell_voltage = (
            electrical_configuration.upper_bound_cell_voltage
        )
        self.used_cell_capacity = electrical_configuration.used_cell_capacity
        self.system_energy = self.nominal_system_voltage * self.system_capacity
        self.workload = kwargs.get("workload", None)
