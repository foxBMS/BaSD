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

"""Implements the command line interface to tbe Battery System Designer tool."""

from dataclasses import dataclass


@dataclass
class CellDimensions:
    """CellDimensions

    :param x: width of the cell
    :param y: length of the cell
    :param z: height of the cell
    """

    x: float
    y: float
    z: float


@dataclass
class RowOffset:
    """RowOffset

    :param first: offset of the first row representation
    :param second: offset of the second row representation
    """

    first: float
    second: float


@dataclass
class InnerPadding:
    """InnerPadding

    :param x: padding between components in x direction
    :param y: padding between components in y direction
    :param z: padding between components in z direction
    """

    x: float
    y: float
    z: float


@dataclass
class OuterPadding:
    """OuterPadding

    :param x: padding between components and bounding box in x direction
    :param y: padding between components and bounding box in y direction
    :param z: padding between components and bounding box in z direction
    """

    x: float
    y: float
    z: float


@dataclass
class ComponentDefinition:  # pylint: disable=too-many-instance-attributes
    """ComponentDefinition

    :param x_pos: position in x direction
    :param y_pos: position in y direction
    :param z_pos: position in z direction
    :param x_dir: number of child components in x direction
    :param y_dir: number of child components in y direction
    :param z_dir: number of child components in z direction
    :param row_offset: offset of the two row representation in y direction
    :param inner_padding: padding between components
    :param outer_padding: padding between components and bounding box
    """

    x_pos: float
    y_pos: float
    z_pos: float
    x_dir: int
    y_dir: int
    z_dir: int
    row_offset: RowOffset
    inner_padding: InnerPadding
    outer_padding: OuterPadding


@dataclass
class ModuleDefinition(ComponentDefinition):
    """ModuleDefinition

    :param alternate: whether the rows should alternate with respect to the cell
        block terminals
    """

    alternate: bool


@dataclass
class CellBlockDefinition(ComponentDefinition):
    """CellBlockDefinition

    :param cell_dimensions: the dimensions of the cell
    :param cell_type: prismatic, cylindric or pouch
    :param rotate: whether the cells should be rotated 90°
    """

    cell_dimensions: CellDimensions
    cell_type: str
    rotate: bool


default_system_definition = {
    "pack_definition": ComponentDefinition(
        0,
        0,
        0,
        0,
        0,
        0,
        RowOffset(0, 0),
        InnerPadding(0, 0, 0),
        OuterPadding(0, 0, 0),
    ),
    "string_definition": ComponentDefinition(
        0,
        0,
        0,
        0,
        0,
        0,
        RowOffset(0, 0),
        InnerPadding(0, 0, 0),
        OuterPadding(0, 0, 0),
    ),
    "module_definition": ModuleDefinition(
        0,
        0,
        0,
        0,
        0,
        0,
        RowOffset(0, 0),
        InnerPadding(0, 0, 0),
        OuterPadding(0, 0, 0),
        False,
    ),
    "cell_block_definition": CellBlockDefinition(
        0,
        0,
        0,
        0,
        0,
        0,
        RowOffset(0, 0),
        InnerPadding(0, 0, 0),
        OuterPadding(0, 0, 0),
        CellDimensions(0, 0, 0),
        "default",
        False,
    ),
}
