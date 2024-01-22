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

"""plot default plugin"""

from pathlib import Path

import matplotlib.pyplot as plt

from basd.simulation.container import Container
from basd.simulation.visualization_api import VisualizationAPI


class PlotResults(VisualizationAPI):  # pylint: disable=too-few-public-methods
    """default plot class of the plugin"""

    @staticmethod
    def plot(containers: list[Container], output: Path) -> None:
        """abstract method for the cyclic aging model

        :param containers: a list of container where container in the list represents
            the simulation results of that specific system
        :param output: path where the plots should be saved
        """
        for container in containers:
            plt.figure("SOH Capacity")
            x = container.time_stamps
            y = [vector["Capacity"] for vector in container.state_vectors]
            plt.plot(x, y)
            plt.title("Aging: System Capacity")
            plt.xlabel("Day")
            plt.ylabel("Capacity (Ah)")
            plt.savefig(output / "capacity.png")
            plt.figure("SOH Internal Resistance")
            x = container.time_stamps
            y = [vector["Internal_Resistance"] for vector in container.state_vectors]
            plt.plot(x, y)
            plt.title("Aging: Internal Resistance")
            plt.xlabel("Day")
            plt.ylabel("Internal Resistance (Ohm)")
            plt.savefig(output / "internal_resistance.png")
            plt.figure("Average Temperature")
            x = container.time_stamps
            y = [vector["Temperature"] for vector in container.state_vectors]
            plt.plot(x, y)
            plt.title("Average Cell Temperature")
            plt.xlabel("Day")
            plt.ylabel("Temperature (degC)")
            plt.savefig(output / "average_cell_temperature.png")
            plt.figure("System SOC")
            x = container.time_stamps
            y = [vector["SOC"] for vector in container.state_vectors]
            plt.plot(x, y)
            plt.title("System SOC")
            plt.xlabel("Day")
            plt.ylabel("SOC (%)")
            plt.savefig(output / "soc.png")
