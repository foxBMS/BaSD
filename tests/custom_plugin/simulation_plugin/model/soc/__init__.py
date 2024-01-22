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

"""Implements simple coulomb counting"""

import sys

from scipy.interpolate import interp1d

from basd.database import BatteryCell


class CoulombCounting:  # pylint: disable=too-few-public-methods
    """Implements a simple coulomb counting algorithm. Based on the cell capacity and an
    initially provided SOC and the, the SOC increase/decrease can be calculated based on
    current and duration."""

    def __init__(
        self,
        ocv: list,
        initial_internal_resistance: float,
        soc: float = 100.0,
    ) -> None:
        """Constructor of the CoulombCounting model

        :ivar ocv: the interpolated ocv of the used cell
        :ivar initial_internal_resistance: the initial internal resistance to model
            the coulomb efficiency of the cell
        :ivar soc: the actual state of char

        """
        if not 0.0 <= soc <= 100.0:
            raise ValueError("SOC must be between 0.0 and 100.0 %")
        self.ocv = interp1d(range(100, -1, -1), ocv)
        self.initial_internal_resistance = initial_internal_resistance
        self.soc = soc
        self.capacity = None

    def calculate(  # pylint: disable=too-many-arguments
        self,
        power: float,
        duration: float,
        capacity: float,
        internal_resistance: float,
    ) -> tuple[float, float, float]:
        """Calculate the current SOC

        :param power: the discharge/charge power of the battery cell
        :param duration: the duration of the actual time step
        :param capacity: the capacity in Ah of the battery cell
        :param internal_resistance: the actual internal resistance of the battery cell
        """
        try:
            voltage = self.ocv(self.soc)
        except ValueError:
            sys.exit(f"SOC: {self.soc}% out of boundary")
        current = power / voltage
        discharged_capacity = current * duration
        capacity = capacity * 3600  # Wh to Ws
        self.soc -= (
            internal_resistance
            / self.initial_internal_resistance
            * ((discharged_capacity / capacity) * 100)
        )
        self.capacity = self.soc / 100 * capacity / 3600  # back to Wh
        return self.capacity, self.soc, current
