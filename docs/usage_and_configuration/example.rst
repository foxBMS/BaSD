.. include:: ./../macros.txt

Examples
========

These examples work with a fictive battery cell on a fictive system:

#. Download the an exemplary, fictive battery cell here is a pdf file
   :download:`Example_Cell.json <../../tests/cells/Example_Cell.json>`.
#. Download the exemplary, fictive requirements file for a system
   :download:`Example-Requirements.json <../../tests/requirements/Example-Requirements.json>`.

.. note::

    Activate the Python environment that |basd| has been install into before
    the next steps.

Example 1
---------

.. warning::

    This example **does** install the example cell in the local database.
    Therefore please make sure to remove the cell from the database after
    finishing this example.
    Please make sure, when following the tutorial, that the paths are adapted
    as needed.

Add the cell to the database and make sure that it installed properly:

.. code-block:: console

   $ basd db add path/to/Example_Cell.json
   $ # list the installed cells
   $ # some additional cells might be listed dependent on your installation
   $ python -m basd db list
     Example:Example_Cell
   $ basd db show Example:Example_Cell
     Cell: Example:Example_Cell
     Identification(manufacturer='Example', model='Example_Cell', manufacturer_safe='Example', model_safe='Example-Cell')
     Mechanics(weight=0.1759211, format='prismatic', standard=False, height=0.0938, length=0.0127, width=0.061799999999999994, volume=7.361986799999999e-05)
     Electrics(capacity=CapacitySpec(initial=14.7536), cont_current=ContinuousCurrentSpec(charge=35.38228910341664, discharge=35.38228910341664), energy=EnergySpec(nominal=55.4882896, minimum=55.4882896), voltage=VoltageSpec(nominal=3.761, minimum=3.0047, maximum=4.1884), discharge_curve=[4.1884, 4.1709, 4.1568, 4.1455, 4.1365, 4.1292, 4.1233, 4.1183, 4.114, 4.1103, 4.1068, 4.1035, 4.0998, 4.0955, 4.0899, 4.0829, 4.0748, 4.0657, 4.056, 4.0459, 4.0356, 4.0251, 4.0147, 4.0043, 3.9942, 3.9845, 3.9752, 3.9663, 3.9578, 3.9498, 3.942, 3.9345, 3.927, 3.9198, 3.9123, 3.9048, 3.8972, 3.8892, 3.881, 3.8726, 3.8635, 3.8529, 3.8363, 3.8192, 3.8056, 3.7938, 3.7829, 3.7726, 3.7626, 3.7529, 3.7434, 3.7344, 3.7259, 3.7177, 3.71, 3.7026, 3.6957, 3.6893, 3.6831, 3.6774, 3.6719, 3.6666, 3.6614, 3.6564, 3.6514, 3.6465, 3.6416, 3.6367, 3.6316, 3.6262, 3.6203, 3.6143, 3.6082, 3.6015, 3.5916, 3.5805, 3.5704, 3.5615, 3.5509, 3.5395, 3.5281, 3.5164, 3.5035, 3.4906, 3.4791, 3.4694, 3.4611, 3.4536, 3.4464, 3.4394, 3.4316, 3.4191, 3.4013, 3.3823, 3.3626, 3.3419, 3.3137, 3.2706, 3.2101, 3.1272, 3.0047])

As next step we can try to create a battery system based on that particular
cell and on the fictive requirements:

.. code-block:: console

   $ basd design -c Example:Example_Cell -r path/to/Example-Requirements.json

The report file ``report.json`` is created in the current working directory.

A CAD design can then be created based on generated report

.. code-block:: console

   $ basd cad -r report.json -f svg 0

This creates a ``svg`` rendering of the first system in the current working
directory.

.. warning::

   The fictive cell should be removed from the database after finishing this
   example.

   .. code-block:: console

      $ basd db rm Example:Example_Cell

Example 2
---------

.. warning::

    This example **does not** install the example cell in the local database.
    Please make sure, when following the tutorial, that the paths are adapted
    as needed.

The battery system can be design using exactly this cell and the example
requirements file:

.. code-block:: console

   $ basd design -r path/to/Example-Requirements.json -d path/to/Example_Cell.json

The report file ``report.json`` is created in the current working directory.

A CAD design can then be created based on generated report

.. code-block:: console

   $ basd cad -r report.json -d path/to/Example_Cell.json -f svg 0

This creates a ``svg`` rendering of the first system in the current working
directory.
