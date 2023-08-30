.. include:: ./../macros.txt

.. _USAGE:

Usage
=====

In order to calculate possible battery system layouts, the tool needs the
following inputs:

- *required*: a database of batteries and their parameters, to test, whether
  the requirements can be fulfilled with any of these batteries
- *required*: the requirements that are forced externally on the system (e.g.,
  the minimum and maximum battery pack voltage)
- *optional*: load profiles the battery system will see during the operation

The general usage workflow for this is as follows:

- The |basd-tool| needs a cell database installation in order to work.
  This needs to be done initially at least once so that battery cells to work
  with are available for the tool.
  However, battery cells can be added to the database at any time.
  The workflow for the database is document :ref:`here <DATABASE_USAGE>`.
- After that a system design dependent on the specific requirements can be
  created using the designer tool.
  Its usage is described :ref:`here <BATTERY_SYSTEM_DESIGNER>`.

  - The output of the designer tool can be 3D rendered using the CAD tool.
    Its usage is described :ref:`here <CAD_USAGE>`.
  - The output of the designer tool can be used as input for a electrical
    simulation.
    Its usage is described :ref:`here <SIMULATION>`.

.. toctree::
   :maxdepth: 1
   :hidden:

   database.rst
   battery-system-designer.rst
   cad.rst
   simulation.rst
