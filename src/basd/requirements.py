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

"""Defines the requirements that can be specified to a battery system."""
import logging
from pathlib import Path

from .utils import validate_json_file


class UnsatisfiableRequirement(Exception):
    """Raised when a requirement can not be sanitized or is physically not meaningful."""


class Requirements:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Holds the battery system requirements"""

    def __init__(self, requirements_file: Path):
        requirements = validate_json_file(requirements_file)
        default_system_requirements = {
            "optimized_by": "volume",
            "only_best": False,
            "cooling": None,
            "cell": {"manufacturer": None, "model": None, "format": None},
        }
        system_requirements = requirements.get("system", default_system_requirements)
        self.cooling = system_requirements.get("cooling", None)
        opt_by = system_requirements.get("optimized_by", None)
        if opt_by is None:
            logging.warning(
                "Optimization variable not specified. "
                "The system will be optimized by volume"
            )
            self.optimized_by = "volume"
        else:
            self.optimized_by = opt_by
        self.only_best = system_requirements.get("only_best", False)
        default_cell_settings = {"manufacturer": None, "model": None, "format": None}
        cell_settings = system_requirements.get("cell", default_cell_settings)
        self.manufacturer = cell_settings.get("manufacturer", None)
        self.model = cell_settings.get("model", None)
        self.format = cell_settings.get("format", None)
        el_req = requirements["electrical"]
        mech_req = requirements["mechanical"]
        self.energy = float(el_req["energy"])
        vol = el_req["voltage"]
        self.nominal_voltage = float(vol["nominal"])
        self.maximum_voltage = float(vol["maximum"])
        self.minimum_voltage = float(vol["minimum"])
        cont = el_req["continuous maximum"]
        self.cont_max_charge_power = float(cont["charge"]["power"])
        self.cont_max_discharge_power = float(cont["discharge"]["power"])
        self.max_module_voltage = float(el_req["maximum module voltage"])
        self.slave_min = int(el_req["slave"].get("minimum", 0))
        self.slave_max = int(el_req["slave"].get("maximum", 100000))
        self.slave_equal = el_req["slave"].get("equal utilization", True)
        self.weight = float(mech_req["weight"])
        self.width = float(mech_req["width"])
        self.height = float(mech_req["height"])
        self.length = float(mech_req["length"])
        self.volume = self.width * self.height * self.length
        self.validate()

    def validate(self) -> None:
        """Validates that the provided requirements are physically meaningfully, e.g.,
        that the minimum voltage can no be higher than the maximum voltage.

        :raises [UnsatisfiableRequirement]: a requirement that is physically not satisfiable.
        """
        if self.optimized_by not in ("volume", "weight"):
            raise UnsatisfiableRequirement("Optimization by unknown criteria.")
        if self.minimum_voltage >= self.maximum_voltage:
            raise UnsatisfiableRequirement(
                "Minium voltage is greater than maximum voltage."
            )
        if not self.minimum_voltage < self.nominal_voltage < self.maximum_voltage:
            raise UnsatisfiableRequirement(
                "Nominal voltage must be between minimum and maximum voltage."
            )

    def __str__(self) -> str:
        """String representation of the requirement."""
        _str = (
            "System Requirements:\n"
            f" Optimized by {self.optimized_by}\n"
            f" only_best {self.only_best}\n"
            f" Cell manufacturer: {self.manufacturer}\n"
            f" Cell model: {self.model}\n"
            f" Cell format: {self.format}\n"
            "Electrical Requirements:\n"
            f" Energy: {self.energy} Wh\n"
            f" Nominal voltage {self.nominal_voltage} V\n"
            f" Minimum voltage {self.minimum_voltage} V\n"
            f" Maximum voltage {self.maximum_voltage} V\n"
            f" Continuous Maximum power {self.cont_max_charge_power} W\n"
            f" Continuous Maximum power {self.cont_max_discharge_power} W\n"
            f" Maximum module voltage {self.max_module_voltage} V\n"
            "Mechanical Requirements:\n"
            f" Weight: {self.weight} kg\n"
            f" Width: {self.width} m\n"
            f" Height: {self.height} m\n"
            f" Length: {self.length} m\n"
        )
        return _str

    def get_requirement_as_table(self) -> list[tuple]:
        """Returns a the requirements in list, that makes it usable as a table."""
        rows = [
            ("Nominal voltage", str(self.nominal_voltage) + " V"),
            ("Maximum voltage", str(self.maximum_voltage) + " V"),
            ("Minimum voltage", str(self.minimum_voltage) + " V"),
            ("Continuous Maximum charge power", str(self.cont_max_charge_power) + " W"),
            (
                "Continuous Maximum discharge power",
                str(self.cont_max_discharge_power) + " W",
            ),
            ("Weight", str(self.weight) + " kg"),
            ("Width", str(self.width) + " m"),
            ("Height", str(self.height) + " m"),
            ("Length", str(self.length) + " m"),
        ]

        return rows
