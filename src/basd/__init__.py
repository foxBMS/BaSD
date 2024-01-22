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

"""Implements the command line interface to the Battery System Designer tool."""
import logging
import multiprocessing
import os
import sys
import warnings
from pathlib import Path
from typing import Optional

import click
import colorama

from .cad import create_cad
from .database import CellDatabase
from .designer import BatterySystemDesigns
from .requirements import Requirements
from .simulation import LifeCycleSimulation
from .utils import (
    BASD_DATABASE_DIR,
    ERROR_MESSAGES,
    get_program_config,
    set_logging_level,
)
from .utils.basd_version import __version__

warnings.simplefilter(action="ignore", category=FutureWarning)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(version=__version__)
@click.option(
    "-s",
    "--show-config",
    default=False,
    is_flag=True,
    help="Shows the program information",
)
@click.pass_context
def main(
    ctx: click.Context,
    show_config: bool,
) -> None:
    """BaSD provides functionalities to design battery system in a pipeline architecture"""
    if show_config:
        config = get_program_config()
        padding = max(len(x) for x in config)
        for key, value in config.items():
            click.echo(f"{key}: {' ' * (padding - len(key))} {value}")
    elif not ctx.invoked_subcommand:
        click.echo(main.get_help(ctx))


@main.group(context_settings=CONTEXT_SETTINGS)
def db() -> None:
    """BaSD database command"""


@db.command(name="list")
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.pass_context
def list_cells(
    ctx: click.Context,
    verbose: int,
) -> None:
    """lists all cell in the database"""
    set_logging_level(verbose)
    cell_database = CellDatabase()
    ctx.exit(cell_database.list_cells())


@db.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.argument("cell_identifiers", nargs=-1, required=True, type=str)
@click.pass_context
def show(ctx: click.Context, verbose: int, cell_identifiers: list[str]) -> None:
    """shows the cell data of a specified cell"""
    set_logging_level(verbose)
    cell_database = CellDatabase()
    ctx.exit(cell_database.show(cell_identifiers))


@db.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.argument(
    "files-to-add",
    nargs=-1,
    required=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, resolve_path=True, path_type=Path
    ),
)
@click.option(
    "-m",
    "--mapping",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    default=None,
    help="Mapping between cell configuration and database",
)
@click.option(
    "-u",
    "--update",
    is_flag=True,
    help="If set, already existing database files are overwritten",
)
@click.pass_context
def add(
    ctx: click.Context,
    verbose: int,
    files_to_add: tuple[Path],
    mapping: Optional[Path],
    update: bool,
) -> None:
    """adds one or more cell data to the database"""
    set_logging_level(verbose)
    database = CellDatabase()
    ctx.exit(database.add(files_to_add, mapping, update))


@db.command(name="rm")
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.argument("cell_identifiers", nargs=-1, required=False, type=str)
@click.option(
    "-a",
    "--all-cells",
    is_flag=True,
    help="Remove all cells in the database",
)
@click.pass_context
def remove(
    ctx: click.Context, verbose: int, cell_identifiers: list[str], all_cells: bool
) -> None:
    """removes one or all cell data in the databases"""
    set_logging_level(verbose)
    if all_cells:
        ctx.exit(CellDatabase.remove_db())
    cell_database = CellDatabase()
    ctx.exit(cell_database.remove(cell_identifiers))


@main.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.option(
    "-r",
    "--requirements",
    "requirements_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    is_eager=True,
    help="Read a battery system configuration from a FILE path.",
)
@click.option(
    "-d",
    "--database",
    type=click.Path(exists=True, path_type=Path),
    default=Path(BASD_DATABASE_DIR),
    is_eager=True,
    help="Read a cell database from a FILE or DIRECTORY path.",
)
@click.option(
    "--report",
    "report_file",
    type=click.Path(exists=False, dir_okay=False, path_type=Path),
    default=(Path(os.getcwd()) / "report"),
    is_eager=True,
    help="Write report file to FILE.",
)
@click.option(
    "--max-number-of-solutions",
    type=int,
    default=100,
    help="Max. number of solutions that should be printed in the report",
)
@click.option(
    "-c",
    "--cell",
    type=str,
    required=False,
    help="Specifies used cell in the system design and additionally overrides settings "
    "(manufacturer and cell model) in requirements",
)
@click.option(
    "--overhead-plugin",
    type=str,
    required=False,
    help="Use a custom overhead implementation. The module needs to be installed in "
    "the same python installation/environment.",
)
@click.option(
    "--cores",
    type=int,
    default=multiprocessing.cpu_count() - 1,
    help="Number of cpu cores used for the calculations.",
)
@click.pass_context
def design(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    verbose: int,
    requirements_file: Path,
    database: Path,
    report_file: Path,
    max_number_of_solutions: int,
    cell: Optional[str],
    overhead_plugin: Optional[str],
    cores: Optional[int],
) -> None:
    """system design task"""
    colorama.init()
    set_logging_level(verbose)

    # load database
    cell_database = CellDatabase(database)

    # get requirements configuration file
    if not requirements_file:
        sys.exit(ERROR_MESSAGES["no-requirements"])
    requirements_file: Path = Path(requirements_file)
    requirement = Requirements(requirements_file)
    if cell is not None:
        manufacturer, model = tuple(cell.split(":"))
        if requirement.manufacturer is not None or requirement.model is not None:
            logging.warning(
                "Requirement settings for manufacturer, cell model "
                "and cell format were overwritten"
            )
        requirement.manufacturer = manufacturer
        requirement.model = model
        requirement.format = None

    bat_sys_variants = BatterySystemDesigns(
        requirement,
        cell_database,
        max_number_of_solutions,
        overhead_plugin,
        cores,
    )
    bat_sys_variants.create_report(report_file)
    ctx.exit(0)


@main.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.argument("system_index", nargs=-1, required=True, type=int)
@click.option(
    "-r",
    "--report",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=(Path(os.getcwd()) / "report"),
    required=True,
    help="Read report file with system designs",
)
@click.option(
    "-f",
    "--output-format",
    type=click.Choice(["step", "svg", "stl"], case_sensitive=True),
    multiple=True,
    required=True,
    help="defines the format of the output. Multiple choices possible",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    default=(Path(os.getcwd())),
    is_eager=True,
    help="Directory in which the output is saved",
)
@click.option(
    "-d",
    "--database",
    type=click.Path(exists=True, path_type=Path),
    default=Path(BASD_DATABASE_DIR),
    help="Read a cell database from a FILE or DIRECTORY path.",
)
@click.pass_context
def cad(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    verbose: int,
    system_index: list[int],
    report: Path,
    database: Path,
    output_dir: Path,
    output_format: list,
) -> None:
    """system design task

    SYSTEM_INDEX specifies which battery system in report file should
    be rendered as CAD model. It can be specified more than one SYSTEM_INDEX. For each
    battery system, the SYSTEM_INDEX can be found as 'Nr.' in the report file.
    """
    colorama.init()
    set_logging_level(verbose)
    step = False
    svg = False
    stl = False
    if "step" in output_format:
        step = True
    if "svg" in output_format:
        svg = True
    if "stl" in output_format:
        stl = True
    # load database
    cell_database = CellDatabase(database)
    svg = False
    opt = {"svg": svg, "step": step, "stl": stl}
    create_cad(
        report,
        cell_database,
        system_index,
        output_dir,
        **opt,
    )
    ctx.exit(0)


@main.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", default=2, count=True, help="Verbose information.")
@click.argument("system_index", nargs=-1, required=True, type=int)
@click.option(
    "-l",
    "--life_cycle",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    required=True,
    help="Profiles to be used for the simulation",
)
@click.option(
    "-r",
    "--report",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    default=(Path(os.getcwd()) / "report.json"),
    required=False,
    help="Read report file with system designs",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    default=(Path(os.getcwd())),
    help="Directory for simulation output",
)
@click.option(
    "-d",
    "--database",
    type=click.Path(exists=True, path_type=Path),
    default=Path(BASD_DATABASE_DIR),
    help="Read a cell database from a FILE or DIRECTORY path.",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default="",
    help="used to pass the name of a custom aging model",
)
@click.option(
    "-p",
    "--plot",
    type=str,
    default="",
    help="used to pass the name of a custom visualization plugin",
)
@click.pass_context
def sim(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    verbose: int,
    system_index: list,
    life_cycle: Path,
    report: Path,
    database: Path,
    **kwargs: dict,
) -> None:
    """system simulation task

    system_index as number of the battery system in the report
    """
    colorama.init()
    set_logging_level(verbose)
    # load database
    cell_database = CellDatabase(database)
    simulation = LifeCycleSimulation(cell_database, report, life_cycle, **kwargs)
    simulation.start(system_index)
    ctx.exit(0)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
