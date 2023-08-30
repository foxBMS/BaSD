##########
Unit tests
##########

To run the unit test suite run the following commands:

.. code-block:: console

   $ # user: activate any conda base environment
   $ conda activate basd-devel-env-11
   $ cd path/to/repo
   $ cd tests
   $ python -m coverage run -m unittest cli_tests.py
   $ python -m coverage html
