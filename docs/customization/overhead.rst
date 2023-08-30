.. include:: ./../macros.txt

.. _OVERHEAD_COMPUTATION:

Overhead Computation
====================

To customize the overhead computation the user needs to implement a plugin.
This plugin can be very simple, i.e., just a single Python script.

- Create a directory, e.g., ``my_plugin``
- Create a setup script ``my_plugin/setup.py`` with the following
  content (``py_modules`` reflects the file file name without the file
  extension):

  .. literalinclude:: ../../tests/custom_plugin/overhead_plugin/setup.py
     :language: python
     :start-after: # START-DOC
     :end-before: # END-DOC
     :caption: Minimal ``setup.py`` for the fictive
               ``custom_overhead_function``-plugin

- Create a new script i.e., ``my_plugin/custom_overhead_function.py``.
  This script needs to implement a class named ``OverheadFunctions`` which
  is derived from ``AbcOverheadFunctions``.
  This class must implement all methods defined in the abstract base class
  :ref:`AbcOverheadFunctions <OVERHEAD_FUNCTIONS_ABC>`.
- Install the plugin in the same Python installation/environment |basd| is
  installed into and check that it is available:

  .. code-block:: console

     $ # activate the environment basd has been installed into
     $ cd my_plugin
     $ python -m pip install .
     $ # check that the plugin has been correctly installed
     $ python -c "import custom_overhead_function; print(custom_overhead_function.OverheadFunctions)"
     <class 'custom_overhead_function.OverheadFunctions'>

- Test the custom plugin against a battery cell (adapt paths to requirements
  and database as needed):

  .. code-block:: console

     basd design -r Example-Requirements.json -d Example_Cell.json --overhead-plugin custom_overhead_function
