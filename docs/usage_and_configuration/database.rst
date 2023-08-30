.. _DATABASE_USAGE:

########
Database
########

Interaction with the battery cell database is done via the subcommand ``db``.

.. program-output:: python -m basd db --help
   :cwd: ../../src


Adding Cells to the Database
############################

- Create a ``json`` file of the cell that shall be added to the database
- Add the required information to the ``json`` file as described in the
  :ref:`CELL_DATABASE` introduction.
- Add the cell to the database (exemplary file name ``my-cell.json``):

  .. code-block:: console

     python -m basd db add my-cell.json

- Done.

From now on, all simulations will also take this cell into account.

Other Database Related Tasks
############################

The database tool supports typical database related tasks, e.g., list all
available cells, show details of a specific cell, or remove cells from the
database etc.
Please use the ``help`` option to display the details.
