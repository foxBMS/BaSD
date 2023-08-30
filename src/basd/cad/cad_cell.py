#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# © 2010 - 2021, Fraunhofer-Gesellschaft zur Foerderung der angewandten Forschung e.V.
# All rights reserved.
"""cad_cell is used to build the CAD object of battery cells

classes:
    Cell
"""

from pathlib import Path

import cadquery as cq

from . import cad_base
from .cad_system_definition import CellDimensions


class Cell(cad_base.BaseCAD):  # pylint: disable=too-few-public-methods
    """Cell is the class to build a CAD object for all three cell types (prismatic,
    cylindrical and pouch)

    :ivar x_pos:  x position of the cell
    :ivar y_pos:  y position of the cell
    :ivar z_pos:  z position of the cell
    :ivar data_json:  Path to json file with cell dimensions
    :ivar key:  identifier of the cell
    :ivar definition: cell definition read from the data_json file
    :ivar rotate: if yes the system is rotated 90 degrees around z-axis

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        cell_type: str,
        dimensions: CellDimensions,
        rotate: bool = False,
    ):
        super().__init__(x_pos, y_pos, z_pos)
        self.dimensions = dimensions
        self.cell_type = cell_type
        if cell_type == "prismatic":
            path_to_standard_model = Path(__file__).parent / Path(
                "cell_dimensions/standard_prismatic.stp"
            )
            degree = 90
            rotation_axis = (1, 0, 0)
        elif cell_type == "cylindrical":
            path_to_standard_model = Path(__file__).parent / Path(
                "cell_dimensions/standard_cylindrical.stp"
            )
            degree = 0
            rotation_axis = (1, 0, 0)
        elif cell_type == "pouch":
            path_to_standard_model = Path(__file__).parent / Path(
                "cell_dimensions/standard_pouch.stp"
            )
            degree = 90
            rotation_axis = (1, 0, 0)
        # rotation needed to orientation the cell with the terminals in z direction
        self.standard_model = cq.importers.importStep(
            str(path_to_standard_model)
        ).rotate((0, 0, 0), rotation_axis, degree)
        standard_bounding_box = self.standard_model.val().BoundingBox()
        self.std_dimensions = (
            standard_bounding_box.xlen,
            standard_bounding_box.ylen,
            standard_bounding_box.zlen,
        )
        self.rotate = rotate

    def create_object(self, alternate: bool = False) -> cq.Workplane:
        """create_object builds based on the cell definition the CAD object of the
        prismatic cell

        :param rotate: should enable battery system rotated 90 degrees
        :param alternate: rotates the cell 180 degree which is used
            for a later serial connection

        :return: workplane object with the prismatic cell on the stack
        """
        result = self.standard_model.translate([self.x_pos, self.y_pos, self.z_pos])
        if alternate:
            if self.cell_type == "cylindrical":
                rotation_degree = 0  # alternating disabled as explained in issue #94
                result = result.rotate((0, 0, 0), (1, 0, 0), rotation_degree)
            else:
                rotation_degree = 0  # alternating disabled as explained in issue #94
                result = result.rotate((0, 0, 0), (0, 0, 1), rotation_degree)
        if self.cell_type == "pouch":
            # CAD model of the pouch cell has switch x and y axes
            result = result.rotate((0, 0, 0), (0, 0, 1), 90)
            matrix = cq.Matrix(
                [
                    [self.dimensions.x / self.std_dimensions[1], 0, 0, 0],
                    [0, self.dimensions.y / self.std_dimensions[0], 0, 0],
                    [0, 0, self.dimensions.z / self.std_dimensions[2], 0],
                    [0, 0, 0, 1],
                ]
            )
        else:
            matrix = cq.Matrix(
                [
                    [self.dimensions.x / self.std_dimensions[0], 0, 0, 0],
                    [0, self.dimensions.y / self.std_dimensions[1], 0, 0],
                    [0, 0, self.dimensions.z / self.std_dimensions[2], 0],
                    [0, 0, 0, 1],
                ]
            )
        result = result.val().transformGeometry(matrix)
        if self.rotate:
            if self.cell_type != "cylindrical":
                rotation_degree = 90
                result = result.rotate((0, 0, 0), (0, 0, 1), rotation_degree)
        result = cq.Workplane().add(result)
        return result
