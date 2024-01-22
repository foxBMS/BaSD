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
"""basd_cad_block contains base functionalities to build CAD object made out of other
CAD objects. For example a battery module is made out of several cell blocks

classes:
    ConfigError
    BlockBasdCAD

functions:
    build_row
    combine
    create_case
    get_center
    get_dimensions
"""

from typing import Optional

import cadquery as cq

from .cad_system_definition import InnerPadding, OuterPadding, RowOffset


class ConfigError(Exception):
    """ConfigError as self defined Exception used configuration errors"""


class BaseCAD:  # pylint: disable=too-few-public-methods
    """BaseCAD class is the base class for all other classes in the CAD tool

    :ivar x_pos: position in x-direction
    :ivar y_pos: position in y-direction
    :ivar z_pos: position in z-direction
    """

    def __init__(self, x_pos: float, y_pos: float, z_pos: float):
        self.x_pos: float = x_pos
        self.y_pos: float = y_pos
        self.z_pos: float = z_pos


class CADBlock(BaseCAD):
    """CADBlock is the base class for the block build (cell_block, module and string)

    :ivar x_pos: x position of the block
    :ivar y_pos: y position of the block
    :ivar z_pos: z position of the block
    :ivar x_dir: number of elements in x direction
    :ivar y_dir: number of elements in y direction
    :ivar z_dir: number of elements in z direction
    :ivar offset: row offset definition as lists in a list ,
    :ivar padding: space to next objects in x,y,z direction
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_dir: int,
        y_dir: int,
        z_dir: int,
        row_offset: RowOffset,
        inner_padding: InnerPadding,
        outer_padding: OuterPadding,
    ):
        super().__init__(x_pos, y_pos, z_pos)
        self.x_dir = x_dir
        self.y_dir = y_dir
        self.z_dir = z_dir
        self.row_offset = row_offset
        self.inner_padding = inner_padding
        self.outer_padding = outer_padding

    def create_object(
        self,
        block_shapes: list[cq.Workplane],
        alternate=False,
    ) -> cq.Workplane:
        """create_object adds a certain number of rows made out of block_shapes in x
        and z direction depending on the values in self.number_of_blocks_in_row to
        the handle

        :param handle: the workplane at which the block_shapes should be added
        :param block_shapes: list of cq.workplanes containing a shape object
        :param alternate: is needed to realize a series connection with cell blocks,
            which need to be rotated alternately in a series connection

        :return: passed handle with the new block_shapes added to the stack
        """
        # row consist out of two element each representing one possible row configuration
        # one row element consist out of several CAD components translated in y-direction
        # the alternating arrangement of the CAD components is the second possible
        # representation of a row
        row = []
        # rows are build by combining the row elements and they represent one layer
        layer = []
        # layers are build by combining the rows elements and they represent the result
        layers = []
        if self.y_dir == 1:
            row.append(block_shapes[0])
            row.append(block_shapes[1])
        else:
            # build "standard" row
            row.append(
                CADBlock.build_row(
                    block_shapes,
                    1,
                    self.inner_padding.y,
                    self.row_offset.first,
                    iterations=self.y_dir,
                )
            )
            # build reversed "alternating" row compared to first row representation
            if alternate:
                block_shapes.reverse()
                row.append(
                    CADBlock.build_row(
                        block_shapes,
                        1,
                        self.inner_padding.y,
                        self.row_offset.second,
                        iterations=self.y_dir,
                    )
                )
        # combine the two representations of the row to one layer
        # if the row should not be alternated then only the first row representation
        # is used to build the one layer
        for i in range(1, self.x_dir + 1):
            if alternate and i % 2 == 0:
                layer.append(row[1])
            else:
                layer.append(row[0])
        if len(layer) > 1:
            layer = CADBlock.build_row(
                layer,
                0,
                self.inner_padding.x,
                offset=0,
            )
        else:
            layer = layer[0]
        layers = [layer] * self.z_dir
        # if statement needed in case block element is two dimensional, because for a
        # two dimensional case self.inner_padding has not three elements
        if len(layers) > 1:
            result = CADBlock.build_row(
                layers,
                2,
                self.inner_padding.z,
                offset=0,
            )
        else:
            result = layers[0]
        return result

    @staticmethod
    def build_row(  # pylint: disable=too-many-arguments
        components: list[cq.Workplane],
        direction: int,
        padding: float,
        offset: float,
        iterations: Optional[int] = None,
        handle: Optional[cq.Workplane] = None,
    ) -> cq.Workplane:
        """build_row builds a row by arranging the passed components alternately
        in a certain direction

        :ivar components: list of cq.Workplane object with shapes in it, which should be
            used to build the row
        :ivar direction: 1 as x direction, 2 as y direction and 3 as z direction
        :ivar iterations: number of components placed in the row
        :ivar padding: space between each component in mm
        :ivar offset: offset at the beginning of the row

        :return: new workplane with all components added to the stack
        """

        def index_comp(ind: int, components: list):
            """used to alternate the component index

            :param ind: index of the component
            :param components: list of cq.Workplane object with shapes in it, which should
                be used to build the row
            """
            return ind % len(components)

        if handle is None:
            handle = cq.Workplane()
        if iterations is None:
            iterations = len(components)
        translation_vector = [0, 0, 0]
        component_dimensions = CADBlock.get_dimensions(components[0])[direction]
        for i in range(iterations):
            component = components[index_comp(i, components)]
            translation_vector[direction] = offset + i * (
                component_dimensions + padding
            )
            handle.add(component.translate(translation_vector))
        return handle

    @staticmethod
    def get_dimensions(components: cq.Workplane, center=False) -> tuple:
        """Return the dimensions of the passed components or if needed
        the center of the components

        :param components: workplane with a shape object on its stack

        :return: width, length and height of the component

        """
        for i, comp in enumerate(components.vals()):
            if i == 0:
                bounding = comp.BoundingBox()
            else:
                bounding = bounding.add(comp.BoundingBox())
        if center:
            return bounding.center
        return bounding.xlen, bounding.ylen, bounding.zlen

    @staticmethod
    def add_box(
        handle: cq.Workplane,
        padding: tuple = None,
        add: tuple = None,
        thickness: float = 0.001,
    ) -> cq.Workplane:
        """adds the "bounding" box surrounding the elements in the passed workplane

        :param handle: the workplane at which the box should be added
        :param padding: padding between box and underlying shapes
        :param thickness: thickness of the box edges, defaults to 0.001
        :return: workplanes with hollowed box around other shapes
        """
        if padding is None:
            padding = [0, 0, 0]
        if add is None:
            add = [0, 0, 0]
        # get dimensions of the all shapes in the workplane
        shapes_dim = CADBlock.get_dimensions(handle)
        # get center of all shapes in the workplane
        center_of_shapes = CADBlock.get_dimensions(handle, center=True)
        final_dim = [
            shapes_dim[i] + padding[i] + add[i] for i in range(len(shapes_dim))
        ]
        box = cq.Workplane("XY").box(*final_dim)
        # cut out everything except the edges
        box = (
            box.faces(">X")
            .center(0, 0)
            .workplane()
            .rect(final_dim[1] - thickness, final_dim[2] - thickness)
            .cutThruAll()
        )
        box = (
            box.faces(">Y")
            .center(0, 0)
            .workplane()
            .rect(final_dim[0] - thickness, final_dim[2] - thickness)
            .cutThruAll()
        )
        box = (
            box.faces(">Z")
            .center(0, 0)
            .workplane()
            .rect(final_dim[0] - thickness, final_dim[1] - thickness)
            .cutThruAll()
        )
        # move hollowed box to center of other shapes
        box = box.translate(center_of_shapes).translate([x / 2 for x in add])
        return handle.add(box)
