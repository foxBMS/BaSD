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

"""data container for the simulation"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Container:
    """Container dataclass used to store the simulated battery system parameter"""

    report_name: str
    system_index: int
    system_design: dict
    __time_stamps: list[float] = field(default_factory=list)
    __state_vectors: list[Any] = field(default_factory=list)

    @property
    def time_stamps(self) -> list[float]:
        """property of the time stamps attribute"""
        return self.__time_stamps

    @property
    def state_vectors(self) -> list[float]:
        """property of the state vectors attribute"""
        return self.__state_vectors

    def get_state_vector(self, time_stamp: float) -> Any:
        """used to get a state vector specified by the time stamp

        :param time_stamp: time_stamp to specify the corresponding state vector
        :return: returns the corresponding state vector
        """
        return self.__state_vectors[self.__time_stamps.index(time_stamp)]

    def __len__(self) -> int:
        """returns the number of stored state vectors"""
        return len(self.__time_stamps)

    def append(self, time_stamp: float, state_vector: Any) -> None:
        """appends a time stamp and a state vector to the container

        :param time_stamp: time_stamp which should be added
        :param state_vector: state_vector corresponding to the time_stamp

        """
        self.__time_stamps.append(time_stamp)
        self.__state_vectors.append(state_vector)
