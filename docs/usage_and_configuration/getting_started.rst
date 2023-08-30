.. include:: ./../macros.txt

.. _GETTING_STARTED:

Getting Started
===============

Installation
------------

The |basd-tool| requires Python 3.10+ to run.
The |basd-tool| has few dependencies, nevertheless it is strongly suggested
that |basd| is installed into a virtual environment.


From pip
^^^^^^^^

The |basd-tool| can be installed by running

.. code-block:: console

   $ # create a new virtual environment and activate it
   $ python -m pip install basd

From sources
^^^^^^^^^^^^

To install the latest development version run

.. code-block:: console

   $ # create a new virtual environment and activate it
   $ python -m pip install git+https://github.com/foxbms/battery-system-designer


Verification
------------

To verify that everything works as expect run, call ``help`` on the BaSD's main
module:

.. code-block:: console

   $ # activate the environment basd has been installed into
   $ basd --help

This should render the following help message on the console

.. program-output:: python -m basd --help
   :cwd: ../../src

Next steps
----------

The :ref:`Usage <USAGE>` sections explains

- how to first add battery cells to the user's database
- how to provide requirements to the design tool
- how to visualize the resulting battery systems
- how to simulate a load profile against the resulting battery systems
