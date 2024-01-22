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

"""Implements simple soh model for the capacity and internal resistance aging process"""

import numpy as np


class SimpleCalendricSOH:  # pylint: disable=R0903
    """Implements a simple SOH model with linear approximation of the aging process."""

    def __init__(
        self,
        aging_rate: float,
        reference_temperature: float = 20.0,
    ) -> None:
        """Constructor of the SimpleCalendricSOH model

        :ivar aging_rate: the slope/rate of the linear aging model
        :ivar reference_temperature: the reference temperature

        """
        self.aging_rate = aging_rate
        self.reference_temperature = reference_temperature

    def calculate(
        self,
        duration: float,
        temperature: float,
        system_property: float,
        increase: bool = False,
    ) -> float:
        """Calculate aging approximated with a linear function

        :param duration: the duration the actual time step
        :param temperature: the temperature of the battery cell during storage
        :param system_property: the actual system property which should be increased/decreased
        :param increase: a switch to set reduction or increase

        :return: new value of the system property

        """
        factor = 1 if increase else -1
        system_property += factor * (
            self.aging_rate
            * (np.abs(temperature / self.reference_temperature))
            * np.sqrt(duration)
        )
        return system_property


class SimpleCyclicSOH:  # pylint: disable=R0903
    """Implements a simple SOH model with linear approximation of the aging process."""

    def __init__(
        self,
        aging_rate: float,
        reference_temperature: float = 20.0,
        reference_current: float = 1.0,
    ) -> None:
        self.aging_rate = aging_rate
        self.reference_temperature = reference_temperature
        self.reference_current = reference_current

    def calculate(  # pylint: disable=too-many-arguments
        self,
        duration: float,
        temperature: float,
        current: float,
        system_property: float,
        increase: bool = False,
    ) -> None:
        """Calculate aging approximated with a linear function

        :param duration: the duration the actual time step
        :param temperature: the temperature of the battery cell during usage
        :param current: current of a battery cell in the system
        :param system_property: the actual system property which should be increased/decreased
        :param increase: a switch to set reduction or increase

        :return: new value of the system property

        """
        factor = 1 if increase else -1
        system_property += factor * np.abs(
            self.aging_rate
            * (current / self.reference_current)
            * (temperature / self.reference_temperature)
            * duration
        )
        return system_property
