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

"""API definition for the aging model"""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BasdModelAPI(ABC):
    """Model API of basd"""

    @abstractmethod
    def get_initial_state_vector(self, system_design: dict) -> Any:
        """abstract method to get the state vector

        :param system_design: the system design as dictionary extracted from the report
        :return: a custom defined state vector for the models should be returned

        """

    @abstractmethod
    def cyclic_aging(
        self,
        state_vector: Any,
        profile: pd.DataFrame,
        ambient_temperature: float,
        system_design: dict,
    ) -> dict:
        """abstract method for the cyclic aging model

        :param state_vector: one specific state vector
        :param profile: a profile as pandas DataFrame
        :param ambient_temperature: the ambient temperature during the usage of the
            battery cell
        :param system_design: the system design as dictionary extracted from the report

        """

    @abstractmethod
    def calendric_aging(
        self, state_vector: Any, duration: int, ambient_temperature: float
    ) -> dict:
        """abstract method for the calendric aging model

        :param state_vector: one specific state vector
        :param duration: the storage duration in days
        :param ambient_temperature: the ambient temperature during the storage of the
            battery cell

        """
