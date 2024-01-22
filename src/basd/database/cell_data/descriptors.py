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

"""Dataclasses to store the physical and meta data of battery cells"""

from dataclasses import dataclass


@dataclass
class Identification:
    """Identification dataclass

    :ivar manufacturer: cell manufacturer name
    :ivar model: cell model name
    :ivar manufacturer_safe: cell manufacturer name with dash instead of whitespace
    :ivar model_safe: cell manufacturer name with dash instead of whitespace
    """

    manufacturer: str
    model: str
    manufacturer_safe: str
    model_safe: str


@dataclass
class Mechanics:
    """Mechanics dataclass

    :ivar weight: the weight of the cell in kg
    :ivar format: cell format as prismatic, cylindrical and pouch
    :ivar standard: a standard like BEV4
    :ivar height: height of the cell in meter
    :ivar length: length of the cell in meter
    :ivar width: width of the cell in meter
    :ivar volume: volume of the cell in m^3
    """

    weight: float
    format: str
    standard: str
    height: float
    length: float
    width: float
    volume: float


@dataclass
class VoltageSpec:
    """VoltageSpec dataclass

    :ivar nominal: nominal cell voltage in V
    :ivar minimum: minimum cell voltage in V
    :ivar maximum: maximum cell voltage in V
    """

    nominal: float
    minimum: float
    maximum: float


@dataclass
class EnergySpec:
    """EnergySpec dataclass

    :ivar nominal: nominal cell energy in Wh
    :ivar minimum: minimum cell energy in Wh
    """

    nominal: float
    minimum: float


@dataclass
class CapacitySpec:
    """CapacitySpec dataclass

    :ivar initial: initial capacity of the battery cell in Ah
    """

    initial: float


@dataclass
class ContinuousCurrentSpec:
    """ContinuousCurrentSpec dataclass

    :ivar charge: maximum charging power of the cell in W
    :ivar discharge: maximum discharge power of the cell in W
    """

    charge: float
    discharge: float


@dataclass
class Electrics:
    """Electrics dataclass

    :ivar capacity: CapacitySpec dataclass
    :ivar cont_current: ContinuousCurrentSpec dataclass
    :ivar energy: EnergySpec dataclass
    :ivar voltage: VoltageSpec dataclass
    :ivar discharge_curve: discharge curve of the battery cell as list

    """

    capacity: CapacitySpec
    cont_current: ContinuousCurrentSpec
    energy: EnergySpec
    voltage: VoltageSpec
    discharge_curve: list
