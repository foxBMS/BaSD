.. include:: ./../macros.txt

Installation
============

User
----

If you just intent to **use** the |basd-tool|, see the
:ref:`Getting Started <GETTING_STARTED>` section to install |basd| as a user.

For Development
---------------

#. Install `VS Code <https://code.visualstudio.com/>`_
#. Set up the development environment:

   .. code-block:: console

      $ # user: activate any conda base environment
      $ conda update -y -n base -c defaults conda
      $ python -m pip install pip --upgrade
      $ conda create -y -n basd-devel-env-11 python=3.10 pip
      $ conda activate basd-devel-env-11
      $ python -m pip install flit --upgrade
      $ git clone https://github.com/foxBMS/BaSD
      $ cd battery-system-designer
      $ python -m flit install --deps all --only-deps

#. Activate the development environment, make changes and run the tools

   .. code-block:: console

      $ # user: activate any conda base environment
      $ conda activate basd-devel-env-11
      $ cd path/to/repo
      $ code .
      $ cd src # testing needs to be run in source directory
      $ python -m basd design -r ../tests/requirements/Example-system.json --database ../tests/cells

Packaging
+++++++++

   .. code-block:: console

      $ # user: activate any conda base environment
      $ conda activate basd-devel-env-11
      $ cd path/to/repo
      $ flit build

Documentation Build
+++++++++++++++++++

   .. code-block:: console

      $ # user: activate any conda base environment
      $ conda activate basd-devel-env-11
      $ cd path/to/repo
      $ cd docs
      $ make html
