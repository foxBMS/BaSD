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

"""overhead functions defines for each element in the battery system the expected
overhead caused by busbar, casing, etc.
"""
from abc import ABC, abstractmethod

import numpy as np

from .basic_sets import BasicParameterSet
from .cooling import Cooling


class AbcOverheadFunctions(ABC):
    """OverheadFunctions class determines the overhead for each battery system
    layout

    :param cooling: the cooling type used in the system
    :param cooling_width: the extra width due to the cooling system
    :param cooling_length: the extra length due to the cooling system
    :param cooling_height: the extra height due to the cooling system
    :param cooling_weight: the extra weight due to the cooling system

    :cvar min_length: minimal length of the battery system
    :cvar min_width: minimal width of the battery system
    :cvar min_height: minimal height of the battery system

    """

    min_length: float = 0.1
    min_width: float = 0.1
    min_height: float = 0.1

    @abstractmethod
    def __init__(self, cooling: Cooling):
        self.cooling: Cooling = cooling
        if cooling == Cooling.AIR:
            self.cooling_width: float = 0.2
            self.cooling_length: float = 0.2
            self.cooling_height: float = 0.0
            self.cooling_weight: float = 0.1
        if cooling == Cooling.GLYCOL:
            self.cooling_width: float = 0.07
            self.cooling_length: float = 0.07
            self.cooling_height: float = 0.0
            self.cooling_weight: float = 0.3
        if cooling == Cooling.REFRIGERANT:
            self.cooling_width: float = 0.03
            self.cooling_length: float = 0.03
            self.cooling_height: float = 0.0
            self.cooling_weight: float = 0.2

    @staticmethod
    def sigmoid(
        x: int, k: float, w: float, a: float, b: float  # pylint: disable=invalid-name
    ) -> float:
        """sigmoid is a mirrored and shifted saturation function to fit the overhead

        :param x: number of specific elements
        :param k: slope of the sigmoid function
        :param w: shift in the x-direction
        :param a: maximum value
        :param b: minimum value

        :return: sigmoid function value for passed x value

        """
        value = (a - b) / (1 + np.exp(k * x - w)) + b
        return value

    @staticmethod
    def linear(x: int, m: float, c: float) -> float:  # pylint: disable=invalid-name
        """a linear function to fit the overhead

        :param x: number of specific elements
        :param m: slope of the sigmoid function
        :param c: intersection point with the y-axis

        :return: linear function value for passed x value
        """
        return m * x + c

    @abstractmethod
    def pack_height(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_height: float,  # pylint: disable=unused-argument
    ) -> tuple[float, bool]:
        """overhead for the pack height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def pack_length(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_length: float,  # pylint: disable=unused-argument
    ) -> tuple[float, bool]:
        """overhead for the pack length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def pack_width(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_width: float,  # pylint: disable=unused-argument
    ) -> tuple[float, bool]:
        """overhead for the pack width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def string_height(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_height: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the string height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def string_length(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_length: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the string length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def string_width(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_width: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the string width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def module_height(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_height: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the module height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def module_length(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_length: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the module length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def module_width(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_width: float,  # pylint: disable=unused-argument
    ) -> float:
        """overhead for the module width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def cell_block_height(self, layout: BasicParameterSet, base_height: float) -> float:
        """overhead for the cell block height

        :param layout: layout parameter
        :param base_height: absolute height caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def cell_block_length(self, layout: BasicParameterSet, base_length: float) -> float:
        """overhead for the cell block length

        :param layout: layout parameter
        :param base_length: absolute length caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def cell_block_width(self, layout: BasicParameterSet, base_width: float) -> float:
        """overhead for the cell block width

        :param layout: layout parameter
        :param base_width: absolute width caused by the number of strings

        :return: overhead

        """

    @abstractmethod
    def pack_gravimetric(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_weight: float,  # pylint: disable=unused-argument
    ) -> float:
        """gravimetric overhead for the pack

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of strings

        :return: overhead
        """

    @abstractmethod
    def string_gravimetric(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_weight: float,  # pylint: disable=unused-argument
    ) -> float:
        """gravimetric overhead for the string

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of modules

        :return: overhead
        """

    @abstractmethod
    def module_gravimetric(
        self,
        layout: BasicParameterSet,  # pylint: disable=unused-argument
        base_weight: float,  # pylint: disable=unused-argument
    ) -> float:
        """gravimetric overhead for the module

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of cell blocks

        :return: overhead
        """

    @abstractmethod
    def cell_block_gravimetric(
        self, layout: BasicParameterSet, base_weight: float
    ) -> float:
        """gravimetric overhead for the cell blocks

        :param layout: layout parameter
        :param base_weight: absolute weight caused by the number of cells

        :return: overhead
        """
