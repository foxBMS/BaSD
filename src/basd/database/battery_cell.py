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

"""Defines the BatteryCell class which holds all relevant data information on a battery cell"""


from .cell_data.descriptors import (
    CapacitySpec,
    ContinuousCurrentSpec,
    Electrics,
    EnergySpec,
    Identification,
    Mechanics,
    VoltageSpec,
)


class UnsupportedCellFormat(Exception):
    """Cell format that is not supported"""


class BatteryCell:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Class to hold all relevant data information on a battery cell

    :ivar identification: all information needed to identify the battery cell
    :ivar mechanics: all mechanical properties of the battery cell
    :ivar electrics: all electrical properties of the battery cell
    """

    def __init__(self, cfg: dict) -> None:
        self.identification = self._add_identification(cfg["identification"])
        self.mechanics = self._add_mechanics(cfg["basics"]["mechanics"])
        self.electrics = self._add_electrics(cfg["basics"]["electrics"])
        for section in cfg:
            if section not in ["basics", "identification"]:
                setattr(self, section, cfg[section])

    def __str__(self) -> str:
        return f"{self.identification.manufacturer}:{self.identification.model}"

    def __repr__(self) -> str:
        return f"{self.identification}\n{self.mechanics}\n{self.electrics}"

    def _add_identification(self, identification: dict) -> Identification:
        """returns the identification properties of the cell read from the dictionary to
        be added to the attributes.

        :return: the identification properties of the cell

        :raise [UnsupportedCellFormat]: if the type of cell is not supported
        """
        man = identification["manufacturer"]
        mod = identification["model"]
        man_safe = "".join(ch if ch.isalnum() else "-" for ch in man)
        mod_safe = "".join(ch if ch.isalnum() else "-" for ch in mod)
        return Identification(man, mod, man_safe, mod_safe)

    def _add_mechanics(self, mechanics: dict) -> Mechanics:
        """returns the mechanical properties of the cell read from the dictionary to be
        added to the attributes.

        :return: the mechanical properties of the battery cell

        :raise [UnsupportedCellFormat]: if the type of cell is not supported
        """
        weight: float = mechanics["weight"]
        cell_format = mechanics["format"].lower()
        standard = mechanics["standard"]
        if not standard:
            standard = False
        if cell_format == "cylindrical":
            height = mechanics["dimensions"]["height"]
            length = mechanics["dimensions"]["length"]
            width = mechanics["dimensions"]["width"]
            volume = height * 3.14 * width**2
            mech = Mechanics(
                weight, cell_format, standard, height, length, width, volume
            )
        elif cell_format == "pouch":
            height = mechanics["dimensions"]["height"]
            length = mechanics["dimensions"]["length"]
            width = mechanics["dimensions"]["width"]
            volume = height * length * width
            mech = Mechanics(
                weight, cell_format, standard, height, length, width, volume
            )
        elif cell_format == "prismatic":
            height = mechanics["dimensions"]["height"]
            length = mechanics["dimensions"]["length"]
            width = mechanics["dimensions"]["width"]
            volume = height * length * width
            mech = Mechanics(
                weight, cell_format, standard, height, length, width, volume
            )
        else:
            raise UnsupportedCellFormat("not supported")
        return mech

    def _add_electrics(self, electrics: dict) -> Electrics:
        """returns the mechanical properties of the cell read from the dictionary to be
        added to the attributes.

        :return: the electrical properties of the battery cell
        """
        voltage_values = electrics["voltage"]
        voltage = VoltageSpec(
            voltage_values["nominal"],
            voltage_values["minimum"],
            voltage_values["maximum"],
        )
        energy_values = electrics["energy"]
        energy = EnergySpec(energy_values["nominal"], energy_values["minimum"])
        capacity = CapacitySpec(electrics["capacity"]["initial"])
        current_values = electrics["current"]
        cont_current = ContinuousCurrentSpec(
            current_values["charge"], current_values["discharge"]
        )
        discharge_curve = electrics["discharge curve"]
        return Electrics(capacity, cont_current, energy, voltage, discharge_curve)
