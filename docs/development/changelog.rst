Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on
`Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Calendar Versioning <https://calver.org/>`_.

[2024.03.0] 2024-03-26
----------------------

Added
^^^^^

- Additionally to the `README.md` also state the acknowledgement in the
  documentation itself.
- Add documentation on how to build the `BaSD` Python package.

[2024.01.1] 2024-01-22
----------------------

Changed
^^^^^^^

- In case a battery cannot be installed from an xml-file, do not raise an
  error, instead issue a warning.
- The implementation of system design process is now facilitation multiple
  cores to speed up the design process.
  This is particularly useful when hundreds or more of cells are considered.
  The default number of cores is `<available_cores> - 1`.
- Removed unused imports.

Fixed
^^^^^

- Fixed a bug in `BasicParameterSet` implementation that showed up in Python
  3.11.
- Minor documentation fixes.
- Developer experience:

  - Updated VS Code settings for latest VS Code releases.
  - Fixed VS Code launcher configurations.

- Fix documentation build via Makefile.
- Fixed project links.

[2023.09.1] 2023-09-05
----------------------

Fixed
^^^^^

- Fixed package number.
- Changelog layout.

[2023.09.0] 2023-09-05
----------------------

Fixed
^^^^^

- Fixed package dependencies.

[2023.08.0] 2023-08-30
----------------------

Added
^^^^^

- Initial release.
