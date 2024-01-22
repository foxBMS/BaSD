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

"""Implements the command line interface to the life cycle simulation"""

import importlib
import inspect
import json
import logging
import sys
from abc import ABCMeta
from pathlib import Path

import pandas as pd

from ..database import CellDatabase
from . import model_api, visualization_api
from .container import Container


class LifeCycleSimulation:  # pylint: disable=R0902,R0903
    """LifeCycleSimulation class implements the framework to simulate a battery"""

    def __init__(  # pylint: disable=too-many-locals
        self,
        database: CellDatabase,
        report: Path,
        life_cycle: Path,
        output_dir: Path,
        **kwargs,
    ):
        """LifeCycleSimulation constructor

        :ivar database: database object to access the cell data
        :ivar report: path where the system designer report can be found
        :ivar life_cycle: file path to the life cycle definition
        :ivar output_dir: path at which the plots should be saved
        :ivar system_designs: all system_designs found in the report as dict
        :ivar path_to_profiles: the path to the folder in which the profiles can be
            found
        :ivar repetition: the number of repetition that should be performed
        :ivar life_cycle: the definition of the life cycle as dictionary without the
            key word repeat
        """
        self.database = database
        self.report = report
        with open(report, mode="r", encoding="utf-8") as f:
            system_designs = json.load(f)
        self.system_designs = list(system_designs)
        self.output_dir = output_dir
        with open(life_cycle, mode="r", encoding="utf-8") as f:
            life_cycle_definition = json.load(f)
        self.path_to_profiles = life_cycle.parent
        self.repetition = life_cycle_definition["repeat"]
        self.life_cycle = {
            period: life_cycle_definition[period]
            for period in life_cycle_definition
            if period != "repeat"
        }
        # import model plugin
        model = kwargs.get("model", "")
        if not model:
            # default model plugin
            model = {"name": ".simulation.model", "package": "basd"}
        try:
            plugin_model = importlib.import_module(**model)
            logging.debug("Using custom aging model implementation '%s'", plugin_model)
        except ModuleNotFoundError as exception:
            logging.error(exception)
            sys.exit(f"Could not import {model}")
        for name, c in inspect.getmembers(plugin_model, inspect.isclass):
            # set the first class fulfilling the requirements as model class
            if name != "BasdModelAPI" and isinstance(c, ABCMeta):
                self.model = c
                break
        plot = kwargs.get("plot", "")
        # import plot plugin
        if not plot:
            # default plot plugin
            plot = {"name": ".simulation.plot", "package": "basd"}
        try:
            plugin_plot = importlib.import_module(**plot)
            logging.debug("Using custom plot implementation '%s'", plugin_plot)
        except ModuleNotFoundError as exception:
            logging.error(exception)
            sys.exit(f"Could not import {plot}")
        for name, c in inspect.getmembers(plugin_plot, inspect.isclass):
            # set the first class fulfilling the requirements as plot class
            if name != "VisualizationAPI" and isinstance(c, ABCMeta):
                plot_class = c
                break
        plot_instance = plot_class()
        if not isinstance(plot_instance, visualization_api.VisualizationAPI):
            sys.exit(
                f"Plot Class {plot} does not properly implement a BaSD visualization API. "
                "Please check the documentation."
            )
        self.plot = plot_class.plot

    def start(  # pylint: disable=too-many-locals
        self, system_indexes: list[int]
    ) -> None:
        """starts the simulation of the system aging process

        :param system_indexes: a list of indexes specifying the system design from a
            report file which should be simulated

        """
        containers = []
        for ind in system_indexes:
            system_design = self.system_designs[ind]
            manufacturer = system_design["Manufacturer"]
            model = system_design["Model"]
            cell_identifier = f"{manufacturer}:{model}"
            # get cell data by cell identifier
            cell_data = self.database.get(cell_identifier)
            model = self.model(cell_data)
            if not isinstance(model, model_api.BasdModelAPI):
                sys.exit(
                    f"Model {model} does not properly implement a BaSD model API. "
                    "Please check the documentation."
                )
            # get from plugin model the state vector definition
            state_vector = model.get_initial_state_vector(system_design)
            container = Container(self.report, ind, system_design)
            container.append(0, state_vector)
            # days are the timestamp of the state vectors
            day = 0
            for _ in range(self.repetition):
                # use last state vector as initial condition of the next simulation step
                if len(container) > 1:
                    state_vector = container.state_vectors[-1]
                for period in self.life_cycle:
                    logging.info("started period %s", period)
                    ambient_temperature = self.life_cycle[period]["temperature"]
                    for part_duration, profile in self._period_parts(period):
                        logging.info("simulate %s", profile)
                        state_vector = model.calendric_aging(
                            state_vector, part_duration, ambient_temperature
                        )
                        day += part_duration
                        container.append(day, state_vector)
                        # a period does not have to end with a usage
                        if profile is not None:
                            # path to profile is a relative path to the life cycle
                            # definition
                            path_to_profile = (
                                self.path_to_profiles / profile
                            ).resolve()
                            profile = pd.read_csv(path_to_profile)
                            state_vector = model.cyclic_aging(
                                state_vector,
                                profile,
                                ambient_temperature,
                                system_design,
                            )
                            # add one day of calendric aging to the cyclic aging
                            state_vector = model.calendric_aging(
                                state_vector, 1, ambient_temperature
                            )
                            day += 1
                            container.append(day, state_vector)
                containers.append(container)
        self.plot(containers, self.output_dir)

    def _period_parts(self, period: dict) -> int:
        """generator to get next calendric duration in period and the profile of the
        following cyclic usage

        :param period: the period definition
        :return: the duration in days of one period part

        """
        period_definition = self.life_cycle[period]
        period_duration = period_definition["duration"]
        last_usage = 0
        for usage in period_definition["usage"]:
            usage_day = int(usage.split(" ")[1])
            if usage_day > period_duration:
                # in case the period definition is defined in a wrong way
                logging.warning("Usage exceeds period duration")
                break
            # minus one, because it is assumed that one usage is maximal one day long
            period_between_usage = usage_day - last_usage - 1
            last_usage = usage_day
            profile = period_definition["usage"][usage]
            yield period_between_usage, profile
        if usage_day < period_duration:
            # returns the last part of the period used by the calendric aging
            yield period_duration - usage_day, None
