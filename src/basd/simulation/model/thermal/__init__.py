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

"""Implements the thermal model of a battery cell"""


class ThermalModel:  # pylint: disable=too-few-public-methods
    """Implementation of a simplified thermal model. Heat dissipation is computed
    using the internal resistance and current

    :ivar heat_capacity: the heat capacity in J/(kgK)
    :ivar surface: the thermal relevant surface of the battery cell in m^2
    :ivar heat_transfer_coefficient: the transfer coefficient in W/(m^2 K)
    :ivar emissivity_factor: ratio between emitted and absorbed radiation
    :ivar temperature: temperature of the battery cell

    """

    def __init__(
        self,
        heat_capacity: float,
        surface: float,
        heat_transfer_coefficient: float,
        emissivity_factor: float,
    ) -> None:
        self.heat_capacity = heat_capacity
        self.surface = surface
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.emissivity_factor = emissivity_factor
        self.temperature = None

    def calculate(  # pylint: disable=too-many-arguments
        self,
        current: float,
        duration: float,
        resistance: float,
        temperature: float,
        surrounding_temperature: float,
    ) -> float:
        """Calculate the current temperature of a cell and append it to the
        previous initialized temperature vector

        :param current: current of the actual simulation step
        :param duration: time step duration
        :param resistance: internal resistance used in the heat generation term
        :param surrounding_temperature: the ambient temperature

        :return: the calculated new temperature
        """
        heat_generation = current**2 * resistance
        heat_transfer_surface = (
            self.heat_transfer_coefficient
            * self.surface
            * ((temperature + 273.14) - (surrounding_temperature + 273.14))
        )
        heat_radiation = (
            self.emissivity_factor
            * 5.670
            * 10 ** (-8)
            * self.surface
            * ((temperature + 273.14) ** 4 - (surrounding_temperature + 273.14) ** 4)
        )
        heat_energy = (
            heat_generation - heat_transfer_surface - heat_radiation
        ) * duration
        self.temperature = temperature + heat_energy / self.heat_capacity
        return self.temperature
