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

"""battery_system provides the class BatterySystemDesigns
"""
import json
import logging
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import interpolate

from ..database import CellDatabase
from ..database.battery_cell import BatteryCell
from ..requirements import Requirements
from .basic_sets import (
    ElectricalConfiguration,
    ElectricalProperties,
    MechanicalProperties,
    Overhead,
)
from .cooling import Cooling
from .find_parameter_sets import find_parameter_sets
from .overhead_functions import OverheadFunctions
from .parameter_set import ParameterSet
from .system_design import SystemDesign


class BatterySystemDesigns:
    """BatterySystemDesigns class as first step in the pipeline finds and ranks possible
    battery system designs"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        requirements: Requirements,
        cell_database: CellDatabase,
        max_number_of_solutions: int,
        overhead_plugin: str,
        cores: int,
    ) -> None:
        """The constructor of the BatterySystemDesigns

        :param requirements: the requirements of the battery system
        :param cell_database: database with the cell information
        :param max_number_of_solutions: the maximal number of solution printed into the
            report
        :param cores: number of cpu cores used for the calculations
        """
        self.requirements = requirements
        self.cell_database = cell_database
        self.max_number_of_solutions = max_number_of_solutions
        considered_cells, overhead_functions = self._filter_inputs_by_settings(
            overhead_plugin
        )
        self.considered_cells = considered_cells
        self.overhead_functions = overhead_functions
        self.system_designs = self.determine_battery_system_designs(cores)

    def determine_battery_system_designs(  # pylint: disable=too-many-locals
        self, cores
    ) -> list:
        """determines all valid battery system designs for all considered cells and
        cooling systems

        :return: a list with all validated battery system designs
        """
        system_designs = []
        result = Parallel(n_jobs=cores, backend="multiprocessing", verbose=1)(
            delayed(self._system_designs_per_cell)(cell, logging.getLogger().level)
            for cell in self.considered_cells
        )
        for system_design in result:
            system_designs.extend(system_design)
        if self.requirements.optimized_by == "volume":
            system_designs.sort(key=lambda x: x.mechanical_properties.volume)
        else:
            system_designs.sort(key=lambda x: x.mechanical_properties.weight)
        if self.requirements.only_best:
            filtered_system_designs = []
            filtered_cells = []
            for system_design in system_designs.copy():
                if system_design.cell not in filtered_cells:
                    filtered_system_designs.append(system_design)
                    filtered_cells.append(system_design.cell)
                    logging.info(
                        "Added best configuration of cell %s", system_design.cell
                    )
                    if set(filtered_cells) == set(self.considered_cells):
                        break
            system_designs = filtered_system_designs
        return system_designs[: self.max_number_of_solutions]

    def create_report(self, report_file_name: Path) -> None:
        """create_report takes the result from determine_possible_systems and creates
        a csv file with all possible systems
        """
        if not getattr(self, "system_designs", None):
            sys.exit("No fitting system found. Please check requirements and settings.")
        columns = [
            "Manufacturer",
            "Model",
            "Format",
            "Cooling type",
            "Cells in parallel",
            "Cells in series",
            "Min. cell voltage (V)",
            "Max. cell voltage (V)",
            "Cell capacity (Ah)",
            "Voltage nom. (V)",
            "Energy (Wh)",
            "Max. module voltage (V)",
            "Min. module voltage (V)",
            "Nom. module voltage (V)",
            "Slave min. workload",
            "Slave max. workload",
            "Number of slaves per modules",
            "Weight (kg)",
            "Volume (m^3)",
            "Length (m)",
            "Width (m)",
            "Height (m)",
            "Cell orientation",
            "Pack z-dir",
            "Pack y-dir",
            "Pack x-dir",
            "String z-dir",
            "String y-dir",
            "String x-dir",
            "Module y-dir",
            "Module x-dir",
            "Cell block y-dir",
            "Cell block x-dir",
            "Overhead height cell block (m)",
            "Overhead height module (m)",
            "Overhead height string (m)",
            "Overhead height pack (m)",
            "Overhead length cell block (m)",
            "Overhead length module (m)",
            "Overhead length string (m)",
            "Overhead length pack (m)",
            "Overhead width cell block (m)",
            "Overhead width module (m)",
            "Overhead width string (m)",
            "Overhead width pack (m)",
            "Overhead weight cell block (kg)",
            "Overhead weight module (kg)",
            "Overhead weight string (kg)",
            "Overhead weight pack (kg)",
            "Overhead height cell block (%)",
            "Overhead height module (%)",
            "Overhead height string (%)",
            "Overhead height pack (%)",
            "Overhead length cell block (%)",
            "Overhead length module (%)",
            "Overhead length string (%)",
            "Overhead length pack (%)",
            "Overhead width cell block (%)",
            "Overhead width module (%)",
            "Overhead width string (%)",
            "Overhead width pack (%)",
            "Overhead weight cell block (%)",
            "Overhead weight module (%)",
            "Overhead weight string (%)",
            "Overhead weight pack (%)",
            "Overall volume overhead (%)",
            "Overall weight overhead (%)",
        ]
        df = pd.DataFrame(columns=columns)
        for i in self.system_designs:
            mech_prop = i.mechanical_properties
            volume_without_overhead = (
                mech_prop.width_without_overhead
                * mech_prop.length_without_overhead
                * mech_prop.height_without_overhead
            )
            row = {
                "Manufacturer": i.cell.identification.manufacturer,
                "Model": i.cell.identification.model,
                "Format": i.cell.mechanics.format,
                "Cooling type": str(i.cooling.name),
                "Cells in parallel": i.electrical_properties.cells_in_parallel,
                "Cells in series": i.electrical_properties.cells_in_series,
                "Min. cell voltage (V)": i.electrical_properties.lower_bound_cell_voltage,
                "Max. cell voltage (V)": i.electrical_properties.upper_bound_cell_voltage,
                "Cell capacity (Ah)": i.electrical_properties.used_cell_capacity,
                "Voltage nom. (V)": i.electrical_properties.nominal_system_voltage,
                "Energy (Wh)": i.electrical_properties.system_energy,
                "Max. module voltage (V)": i.electrical_properties.max_module_voltage,
                "Min. module voltage (V)": i.electrical_properties.min_module_voltage,
                "Nom. module voltage (V)": i.electrical_properties.nom_module_voltage,
                "Slave min. workload": i.electrical_properties.workload.min,
                "Slave max. workload": i.electrical_properties.workload.max,
                "Number of slaves per modules": i.electrical_properties.workload.slaves,
                "Weight (kg)": mech_prop.weight,
                "Volume (m^3)": mech_prop.volume,
                "Length (m)": mech_prop.length,
                "Width (m)": mech_prop.width,
                "Height (m)": mech_prop.height,
                "Cell orientation": "0°" if i.layout.cell_rotation == 0 else "90°",
                "Pack z-dir": i.layout.pack.z,
                "Pack y-dir": i.layout.pack.y,
                "Pack x-dir": i.layout.pack.x,
                "String z-dir": i.layout.string.z,
                "String y-dir": i.layout.string.y,
                "String x-dir": i.layout.string.x,
                "Module y-dir": i.layout.module.y,
                "Module x-dir": i.layout.module.x,
                "Cell block y-dir": i.layout.cell_block.y,
                "Cell block x-dir": i.layout.cell_block.x,
                "Overhead height cell block (m)": mech_prop.height_overhead.cell_block[
                    0
                ],
                "Overhead height module (m)": mech_prop.height_overhead.module[0],
                "Overhead height string (m)": mech_prop.height_overhead.string[0],
                "Overhead height pack (m)": mech_prop.height_overhead.pack[0],
                "Overhead length cell block (m)": mech_prop.length_overhead.cell_block[
                    0
                ],
                "Overhead length module (m)": mech_prop.length_overhead.module[0],
                "Overhead length string (m)": mech_prop.length_overhead.string[0],
                "Overhead length pack (m)": mech_prop.length_overhead.pack[0],
                "Overhead width cell block (m)": mech_prop.width_overhead.cell_block[0],
                "Overhead width module (m)": mech_prop.width_overhead.module[0],
                "Overhead width string (m)": mech_prop.width_overhead.string[0],
                "Overhead width pack (m)": mech_prop.width_overhead.pack[0],
                "Overhead weight cell block (kg)": mech_prop.weight_overhead.cell_block[
                    0
                ],
                "Overhead weight module (kg)": mech_prop.weight_overhead.module[0],
                "Overhead weight string (kg)": mech_prop.weight_overhead.string[0],
                "Overhead weight pack (kg)": mech_prop.weight_overhead.pack[0],
                "Overhead height cell block (%)": mech_prop.height_overhead.cell_block[
                    1
                ],
                "Overhead height module (%)": mech_prop.height_overhead.module[1],
                "Overhead height string (%)": mech_prop.height_overhead.string[1],
                "Overhead height pack (%)": mech_prop.height_overhead.pack[1],
                "Overhead length cell block (%)": mech_prop.length_overhead.cell_block[
                    1
                ],
                "Overhead length module (%)": mech_prop.length_overhead.module[1],
                "Overhead length string (%)": mech_prop.length_overhead.string[1],
                "Overhead length pack (%)": mech_prop.length_overhead.pack[1],
                "Overhead width cell block (%)": mech_prop.width_overhead.cell_block[1],
                "Overhead width module (%)": mech_prop.width_overhead.module[1],
                "Overhead width string (%)": mech_prop.width_overhead.string[1],
                "Overhead width pack (%)": mech_prop.width_overhead.pack[1],
                "Overall volume overhead (%)": mech_prop.volume
                / volume_without_overhead
                * 100
                - 100,
                "Overhead weight cell block (%)": mech_prop.weight_overhead.cell_block[
                    1
                ],
                "Overhead weight module (%)": mech_prop.weight_overhead.module[1],
                "Overhead weight string (%)": mech_prop.weight_overhead.string[1],
                "Overhead weight pack (%)": mech_prop.weight_overhead.pack[1],
                "Overall weight overhead (%)": mech_prop.weight
                / mech_prop.weight_without_overhead
                * 100
                - 100,
            }
            df.loc[len(df)] = row
        # cast specific columns to numeric values to control the float point precision
        # in the report
        columns_with_units = [x for x in df.columns if "(" in x and ")" in x]
        df.loc[:, columns_with_units] = df.loc[:, columns_with_units].apply(
            pd.to_numeric, errors="coerce", axis=1
        )
        df = df.round(2)
        out_csv = Path(f"{report_file_name}.csv")
        df.to_csv(out_csv, sep=",", float_format="%.2f", index=True)
        df.insert(0, "Nr.", df.index)
        dict_df = df.to_dict("records")
        out_json = Path(f"{report_file_name}.json")
        with open(out_json, mode="w", encoding="utf-8") as f:
            json.dump(dict_df, f, indent=4, ensure_ascii=False)

    def _determine_battery_system_configuration(  # pylint: disable=too-many-locals
        self, cell_data: BatteryCell
    ) -> ElectricalConfiguration:
        """determines all relevant parameter of the electrical configuration

        :param requirements: requirements object with all defined requirements of the
            battery system
        :param cell_data: the data of one specific cell
        :return: relevant parameter of the electrical configuration of
            the battery system
        """
        cells_in_series = np.ceil(
            self.requirements.nominal_voltage / cell_data.electrics.voltage.nominal
        )
        nominal_system_voltage = cells_in_series * cell_data.electrics.voltage.nominal
        min_system_voltage = cells_in_series * cell_data.electrics.voltage.minimum
        if min_system_voltage < self.requirements.minimum_voltage:
            lower_bound_cell_voltage = (
                self.requirements.minimum_voltage / cells_in_series
            )
        else:
            lower_bound_cell_voltage = cell_data.electrics.voltage.minimum
        max_system_voltage = cells_in_series * cell_data.electrics.voltage.maximum
        if max_system_voltage > self.requirements.maximum_voltage:
            upper_bound_cell_voltage = (
                self.requirements.maximum_voltage / cells_in_series
            )
        else:
            upper_bound_cell_voltage = cell_data.electrics.voltage.maximum
        soc = list(range(0, 101))[::-1]
        f_soc = interpolate.interp1d(
            cell_data.electrics.discharge_curve, soc, bounds_error=True
        )
        lower_soc = f_soc(lower_bound_cell_voltage)
        upper_soc = f_soc(upper_bound_cell_voltage)
        used_cell_capacity = (
            (upper_soc - lower_soc) / 100 * cell_data.electrics.capacity.initial
        )
        required_system_capacity = self.requirements.energy / nominal_system_voltage
        cells_in_parallel = np.ceil(required_system_capacity / used_cell_capacity)
        max_discharge_power = (
            cells_in_parallel
            * cell_data.electrics.cont_current.discharge
            * nominal_system_voltage
        )
        if max_discharge_power <= self.requirements.cont_max_discharge_power:
            cells_in_parallel = np.ceil(
                self.requirements.cont_max_discharge_power
                / nominal_system_voltage
                / cell_data.electrics.cont_current.discharge
            )
        max_charge_power = (
            cells_in_parallel
            * cell_data.electrics.cont_current.charge
            * nominal_system_voltage
        )
        if max_charge_power <= self.requirements.cont_max_charge_power:
            cells_in_parallel = np.ceil(
                self.requirements.cont_max_charge_power
                / nominal_system_voltage
                / cell_data.electrics.cont_current.charge
            )
        system_capacity = cells_in_parallel * used_cell_capacity
        electrical_configuration = ElectricalConfiguration(
            int(cells_in_parallel),
            int(cells_in_series),
            nominal_system_voltage,
            system_capacity,
            lower_bound_cell_voltage,
            upper_bound_cell_voltage,
            used_cell_capacity,
            system_capacity * nominal_system_voltage,
        )
        return electrical_configuration

    def _check_upper_bounds(  # pylint: disable=too-many-locals, too-many-branches
        self, list_of_parameter_sets: list[ParameterSet]
    ) -> tuple[list[ParameterSet], list[dict[str, Overhead]]]:
        """checks the parameter set for upper bound conditions

        :param list_of_parameter_sets: a list with the parameter sets fulfilling the
            lower bound condition from the electrical configuration
        :return: a tuple with the validated parameter sets and their overheads
        """
        validated_parameter_sets = []
        mechanical_properties = []
        module_voltages = []
        slave_utils = []
        number_of_parameter_sets = len(list_of_parameter_sets)

        for i, parameter_set in enumerate(list_of_parameter_sets):
            logging.debug(
                "Check parameter set number %s of %s", i, number_of_parameter_sets
            )
            module_voltage = parameter_set.get_maximum_module_voltage()
            if module_voltage >= self.requirements.max_module_voltage:
                continue
            bjb = False
            dimensions = {}
            # first it is tried to place the bjb in length direction, then in width
            # direction and last in height direction
            # if bjb variable is never set to true, the loop will go to the next
            # parameter set
            for dim in ["length", "width", "height"]:
                value, overhead = getattr(parameter_set, f"get_{dim}")(bjb=not bjb)
                if value >= getattr(self.requirements, dim):
                    if not bjb:
                        value, overhead = getattr(parameter_set, f"get_{dim}")(
                            bjb=False
                        )
                        if value >= getattr(self.requirements, dim):
                            break
                    else:
                        break
                else:
                    bjb = True
                dimensions[dim] = value
                dimensions[f"{dim}_overhead"] = overhead
            if len(dimensions) < 6:
                continue
            if not bjb:
                logging.warning(
                    "Overhead Functions: Battery junction box not consider in any direction"
                )
                continue
            weight, weight_overhead = parameter_set.get_weight()
            if weight >= self.requirements.weight:
                continue
            # check slave requirement
            slave_util = parameter_set.get_slave_utilization(
                self.requirements.slave_max
            )
            if slave_util is not None and (
                # not fulfilling the requirements
                slave_util.min < self.requirements.slave_min
                or slave_util.max > self.requirements.slave_max
            ):
                # in case the workload per slave has to be equalized
                if self.requirements.slave_equal and slave_util.max != slave_util.min:
                    continue
                continue
            validated_parameter_sets.append(parameter_set)
            # calculate mechanical system properties without overhead
            height_without_overhead = (
                parameter_set.cell.mechanics.height
                * parameter_set.string.z
                * parameter_set.pack.z
            )
            length_without_overhead = (
                parameter_set.cell.mechanics.length
                * parameter_set.pack.y
                * parameter_set.string.y
                * parameter_set.module.y
                * parameter_set.cell_block.y
            )
            width_without_overhead = (
                parameter_set.cell.mechanics.width
                * parameter_set.pack.x
                * parameter_set.string.x
                * parameter_set.module.x
                * parameter_set.cell_block.x
            )
            weight_without_overhead = (
                parameter_set.cell.mechanics.weight
                * parameter_set.pack.x
                * parameter_set.pack.y
                * parameter_set.pack.z
                * parameter_set.string.x
                * parameter_set.string.y
                * parameter_set.string.z
                * parameter_set.module.x
                * parameter_set.module.y
                * parameter_set.cell_block.x
                * parameter_set.cell_block.y
            )
            mechanical_properties_of_one_set = MechanicalProperties(
                dimensions["height"],
                dimensions["length"],
                dimensions["width"],
                weight,
                dimensions["height_overhead"],
                dimensions["length_overhead"],
                dimensions["width_overhead"],
                weight_overhead,
                height_without_overhead,
                length_without_overhead,
                width_without_overhead,
                weight_without_overhead,
            )
            mechanical_properties.append(mechanical_properties_of_one_set)
            module_voltages.append(module_voltage)
            slave_utils.append(slave_util)
        return (
            validated_parameter_sets,
            mechanical_properties,
            module_voltages,
            slave_utils,
        )

    def _filter_inputs_by_settings(
        self, overhead_plugin: str = ""
    ) -> tuple[BatteryCell, OverheadFunctions]:
        """the used cells and overhead factors are filtered by the settings

        :returns: tuple with filter cells information and overhead factors
        """
        overhead = self._get_overhead_functions(overhead_plugin)
        if self.requirements.cooling is not None:
            overhead_functions = [
                overhead(x) for x in Cooling if self.requirements.cooling in str(x)
            ]
        else:
            overhead_functions = [overhead(x) for x in Cooling]
        # reduces the number of used cells in the optimization step
        # filter can be set in settings file default=config/basd_settings.json
        considered_cells = self.cell_database.cells
        if self.requirements.manufacturer is not None:
            considered_cells = [
                x
                for x in considered_cells
                if x.identification.manufacturer == self.requirements.manufacturer
            ]
        if self.requirements.model is not None:
            considered_cells = [
                x
                for x in considered_cells
                if x.identification.model == self.requirements.model
            ]
        if self.requirements.format is not None:
            considered_cells = [
                x
                for x in considered_cells
                if x.mechanics.format == self.requirements.format
            ]
        if not considered_cells:
            logging.warning(
                "Number of cells considered to build battery systems is zero. "
                "Please check requirement settings and database"
            )
        return considered_cells, overhead_functions

    def _system_designs_per_cell(  # pylint: disable=too-many-locals
        self, cell: BatteryCell, log_level: int
    ) -> list[SystemDesign]:
        """TODO"""
        logging.getLogger().setLevel(log_level)
        system_designs_per_cell = []
        logging.info("Process %s", cell)
        # get electrical system configuration
        electrical_configuration = self._determine_battery_system_configuration(cell)
        logging.debug(electrical_configuration)
        start_parameter = [1, 1, 1, 1, 1]
        # get all possible parameters for the series connection
        parameters_series = find_parameter_sets(
            start_parameter,
            lambda x: np.prod(x)
            >= electrical_configuration.cells_in_series,  # pylint: disable=cell-var-from-loop
        )
        start_parameter = [1, 1, 1, 1, 1]
        # get all possible parameters for the parallel connection
        parameters_parallel = find_parameter_sets(
            start_parameter,
            lambda x: np.prod(x)
            >= electrical_configuration.cells_in_parallel,  # pylint: disable=cell-var-from-loop
        )
        parameter_sets = []
        cell_rotation = (0, 1)  # 0=0° or 1=90° cell rotation
        # overhead functions is a list with a overhead definition for each cooling type
        for cart_product in product(
            self.overhead_functions,
            parameters_series,
            parameters_parallel,
            cell_rotation,
        ):
            parameter_set = ParameterSet(
                cell=cell, overhead=cart_product[0], requirements=self.requirements
            )  # overhead
            parameter_set["series"] = cart_product[1]  # series
            parameter_set["parallel"] = cart_product[2]  # parallel
            parameter_set.cell_rotation = cart_product[3]  # rotation
            parameter_sets.append(parameter_set)
            logging.debug(parameter_set)
        (
            validated_parameter_sets,
            mechanical_properties,
            max_module_voltages,
            workloads,
        ) = self._check_upper_bounds(parameter_sets)
        # initialize all validated system designs
        for i, parameter_set in enumerate(validated_parameter_sets):
            electrical_property = ElectricalProperties(
                parameter_set,
                electrical_configuration,
                max_module_voltage=max_module_voltages[i],
                workload=workloads[i],
            )
            mechanical_property = mechanical_properties[i]
            system_design = SystemDesign(
                parameter_set,
                mechanical_property,
                electrical_property,
            )
            system_designs_per_cell.append(system_design)
        return system_designs_per_cell

    @staticmethod
    def _get_overhead_functions(overhead_plugin: str = ""):
        if overhead_plugin:
            import importlib  # pylint: disable=import-outside-toplevel

            try:
                plugin = importlib.import_module(overhead_plugin)
                logging.debug("Using custom overhead implementation '%s'", plugin)
            except ModuleNotFoundError:
                sys.exit("Could not find %s", overhead_plugin)
            if not hasattr(plugin, "OverheadFunctions"):
                sys.exit(
                    f"Plugin {overhead_plugin} does not implement a class called "
                    "'OverheadFunctions'.\nPlease check the documentation."
                )
            return plugin.OverheadFunctions
        return OverheadFunctions
