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

"""file containing the solver for the optimization of the integer program
"""

from itertools import permutations
from typing import Callable

import numpy as np


def find_parameter_sets(
    parameter: list,
    validation_func: Callable,
) -> list[list]:
    """find_parameter_sets executes a modified backtracking algorithms to find all
    validated parameter sets

    :param parameter: an initial parameter set
    :param validation_func: a function to validate the current parameter_set

    :return: a list of all validated parameter sets
    """

    def next_branch(parameter: list, level: int) -> list:
        """the next_branch function increases the parameter in the level and
        sets all others to 1, which can be interpreted as switching to the next upper
        branch in the backtracking algorithm

        :param parameter: a list with parameter
        :param level: each parameter with its index represent a level in a search tree

        :returns: new set of parameter

        """
        parameter[level] += 1
        for i in range(level):
            parameter[i] = 1
        return parameter

    # condition to stop the backtracking algorithm
    # max_level is max_index in uml diagram
    max_level = len(parameter) - 1
    # condition the move to the next upper branch in the search tree
    max_value = np.inf
    level = 0
    parameter_list = []
    while True:
        max_para = max(parameter)
        # if false move to next upper branch
        if max_para <= max_value:
            # test all validation function
            if validation_func(parameter):
                parameter_list.append(parameter.copy())
                max_value = max(parameter) - 1
                level += 1
                parameter = next_branch(parameter, level)
                level = 0
            else:
                parameter[level] += 1
        else:
            level = parameter.index(max_para) + 1
            if level > max_level:
                break
            parameter = next_branch(parameter, level)
            level = 0
    solution = []
    # add to found solution all permutations
    for para in parameter_list:
        # the set cast speeds up the whole permutation process
        solution.extend(list(set(permutations(para))))
    return solution
