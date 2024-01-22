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

"""Helper script to retrieve the paths to logos."""

import os
import sys
from pathlib import Path

IS_SPHINX_BUILD = f"{os.sep}sphinx" in sys.argv[0]

if IS_SPHINX_BUILD:
    #: location of the the script on the file system
    SCRIPT_DIR = Path("${install_path/utils}").as_posix()
    #: path to the BaSD logo
    BASD_LOGO = (Path(SCRIPT_DIR) / ".." / "_static" / "basd-logo.png").as_posix()
    #: path to the Fraunhofer IISB logo
    IISB_LOGO = (
        Path(SCRIPT_DIR) / ".." / "_static" / "fraunhofer-iisb-logo.png"
    ).as_posix()
else:
    #: location of the the script on the file system
    SCRIPT_DIR = Path(__file__).resolve().parent
    #: path to the BaSD logo
    BASD_LOGO = SCRIPT_DIR / ".." / "_static" / "basd-logo.png"
    #: path to the Fraunhofer IISB logo
    IISB_LOGO = SCRIPT_DIR / ".." / "_static" / "fraunhofer-iisb-logo.png"
