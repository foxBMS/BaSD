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

"""Implements the example aging model"""

import logging

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from basd.database import cell_data
from basd.designer.system_design import SystemDesign
from basd.simulation.model_api import BasdModelAPI

from .soc import CoulombCounting
from .soh import SimpleCalendricSOH, SimpleCyclicSOH
from .thermal import ThermalModel


class AgingModel(BasdModelAPI):
    """Example aging model class with a rudimentary electric, thermal and soh
    model/approximation

    """

    def __init__(self, cell: cell_data):
        """Constructor of the AgingModel

        :ivar cell: one specific cell for which the simulation should be done
        :ivar coulomb: the initiated electrical model (Coulomb model)
        :ivar thermal: the thermal model
        :ivar soh_cyclic_cap: the cyclic aging capacity model
        :ivar soh_cyclic_res: the cyclic aging internal resistance model
        :ivar soh_calendric_cap: the calendric aging capacity model
        :ivar soh_calendric_res: the calendric aging internal resistance model
        """
        self.cell = cell
        self.coulomb = CoulombCounting(
            self.cell.electrics.discharge_curve, cell.simulation["internal_resistance"]
        )
        if cell.mechanics.format in ("Prismatic", "Pouch"):
            # cooling from below
            surface_of_one_cell = (
                cell.basics.mechanics.length * cell.basics.mechanics.width
            )
        else:
            # cooling from on side hence half lateral surface
            surface_of_one_cell = (
                cell.mechanics.length * np.pi * cell.mechanics.height / 2
            )
        self.thermal = ThermalModel(
            cell.simulation["heat_capacity"] * cell.mechanics.weight,
            surface_of_one_cell,
            cell.simulation["heat_transfer_coefficient"],
            cell.simulation["emissivity_factor"],
        )
        self.soh_cyclic_cap = SimpleCyclicSOH(
            aging_rate=self.cell.simulation["cyclic_aging_rate_cap"]
        )
        self.soh_cyclic_res = SimpleCyclicSOH(
            aging_rate=self.cell.simulation["cyclic_aging_rate_res"]
        )
        self.soh_calendric_cap = SimpleCalendricSOH(
            aging_rate=self.cell.simulation["calendric_aging_rate"]
        )
        self.soh_calendric_res = SimpleCalendricSOH(
            aging_rate=self.cell.simulation["calendric_aging_rate"]
        )

    def get_initial_state_vector(self, system_design: dict) -> dict:
        """returns the initial vector of the example aging model

        :param system_design: the system design extracted from the report as dict
        :return: the initial state vector
        """
        initial_state_vector = {
            "SOC": 100,
            "Capacity": system_design["Cell capacity (Ah)"]
            * system_design["Cells in parallel"],
            "Internal_Resistance": system_design["Cells in series"]
            * self.cell.simulation["internal_resistance"],
            "Temperature": 0,
        }
        return initial_state_vector

    def cyclic_aging(  # pylint: disable=too-many-locals
        self,
        state_vector: dict,
        profile: pd.DataFrame,
        ambient_temperature: float,
        system_design: SystemDesign,
    ) -> dict:
        """cyclic aging

        :param state_vector: the state vector at a specific point of time
        :param profile: the profile which should be used for the cyclic aging
        :param ambient_temperature: ambient temperature
        :param system_design: the system design as dictionary

        :return: the next state vector

        """
        number_of_cells = (
            system_design["Cells in parallel"] * system_design["Cells in series"]
        )
        time_step = 1
        x = list(profile["Timestamp_s"])
        y = list(profile["Power_W"])
        # ensure profile start with time step 0
        if x[0] >= 0:
            x.insert(0, 0.0)
            y.insert(0, y[0])
        profile_interpolation = interp1d(x, y, kind="previous")
        number_of_iterations = int(np.floor(x[-1] / time_step))
        previous_current = 0
        previous_temperature = ambient_temperature
        temperature_sum = previous_temperature
        for i in range(0, number_of_iterations):
            new_state_vector = state_vector.copy()
            power = profile_interpolation(i * time_step)
            # get parameter related to one cell
            power_per_cell = power / number_of_cells
            capacity_per_cell = (
                state_vector["Capacity"] / system_design["Cells in parallel"]
            )
            internal_resistance_per_cell = (
                state_vector["Internal_Resistance"] / system_design["Cells in series"]
            )
            # simulate soc for one cell
            _, soc, current = self.coulomb.calculate(
                power_per_cell,
                time_step,
                capacity_per_cell,
                internal_resistance_per_cell,
            )
            new_state_vector["SOC"] = soc
            # simulated temperature of one cell
            temperature = self.thermal.calculate(
                current,
                time_step,
                internal_resistance_per_cell,
                previous_temperature,
                ambient_temperature,
            )
            # simulate soh for one cell
            new_capacity_per_cell = self.soh_cyclic_cap.calculate(
                time_step, previous_temperature, previous_current, capacity_per_cell
            )
            new_state_vector["Capacity"] = (
                new_capacity_per_cell * system_design["Cells in parallel"]
            )
            new_internal_resistance_per_cell = self.soh_cyclic_res.calculate(
                time_step,
                previous_temperature,
                previous_current,
                internal_resistance_per_cell,
                increase=True,
            )
            new_state_vector["Internal_Resistance"] = (
                new_internal_resistance_per_cell * system_design["Cells in series"]
            )
            previous_current = current
            previous_temperature = temperature
            temperature_sum += temperature
            state_vector = new_state_vector
        state_vector["Temperature"] = temperature_sum / number_of_iterations
        logging.info("actual state: %s", str(state_vector))
        return new_state_vector

    def calendric_aging(
        self, state_vector: dict, duration: int, ambient_temperature: float
    ) -> dict:
        """calendric aging

        :param state_vector: the state vector at a specific point of time
        :param ambient_temperature: ambient temperature

        :return: the next state vector
        """
        new_state_vector = state_vector.copy()
        new_state_vector["Capacity"] = self.soh_calendric_cap.calculate(
            duration, ambient_temperature, state_vector["Capacity"]
        )
        new_state_vector["Internal_Resistance"] = self.soh_calendric_res.calculate(
            duration, ambient_temperature, state_vector["Internal_Resistance"]
        )
        return new_state_vector
