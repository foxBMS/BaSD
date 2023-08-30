.. include:: ./../macros.txt

.. _MECHANICAL_OVERHEAD:

###################
Mechanical Overhead
###################

Levels of Freedom in Layouting Battery System Configurations
############################################################

- For **cells** the following levels of freedom exist to combine them to
  **cell blocks** in space are shown below.

  - The number of cells in a row is denoted by C\ :sub:`R`.
  - The number of rows is denoted by C\ :sub:`N`.

  .. figure:: cell-block.png
     :alt: Cell block

- For **cells blocks** the following levels of freedom exist to combine them to
  **modules** in space are shown below.

  - The number of cell blocks in a row is denoted by M\ :sub:`R`.
  - The number of rows is denoted by M\ :sub:`N`.

  .. figure:: module.png
     :alt: module

- For **modules** the following levels of freedom exist to combine them to
  **strings** in space are shown below.

  - The number of modules in a row is denoted by S\ :sub:`R`.
  - The number of rows is denoted by S\ :sub:`N`.
  - The number of layers is denoted by S\ :sub:`L`.

  .. figure:: string.png
     :alt: string

- For **strings** the following levels of freedom exist to combine them to a
  **pack** in space are shown below.

  - The number of strings in a row is denoted by **P**\ :sub:`R`.
  - The number of rows is denoted by **P**\ :sub:`N`.
  - The number of layers is denoted by **P**\ :sub:`L`.

  .. figure:: pack.png
     :alt: pack

- Introduction of overhead factors **O**
- Overhead factors describe additional weight and volume caused by the cooling
  system, busbars, contactors,
- Definition of the system dimensions:

 - The cell width is defined as: C\ :sub:`width`
 - The cell length is defined as: C\ :sub:`length`
 - The cell height is defined as: C\ :sub:`height`

- Pack width:  **P**\ :sub:`W` = **P**\ :sub:`N` * **O**\ :sub:`PN` * **S**\ :sub:`N` * **O**\ :sub:`SN` * **M**\ :sub:`N` * **O**\ :sub:`MN` * **C**\ :sub:`N` * **O**\ :sub:`CN` * **C**\ :sub:`width`
- Pack length: **P**\ :sub:`L` = **P**\ :sub:`R` * **O**\ :sub:`PR` * **S**\ :sub:`R` * **O**\ :sub:`SR` * **M**\ :sub:`R` * **O**\ :sub:`MR` * **C**\ :sub:`R` * **O**\ :sub:`CR` * **C**\ :sub:`width`
- Pack height: **P**\ :sub:`H` = **P**\ :sub:`L` * **O**\ :sub:`PL` * **S**\ :sub:`L` * **O**\ :sub:`SL` * **C**\ :sub:`height`
- Pack volume: **P**\ :sub:`V` = **P**\ :sub:`L` * **P**\ :sub:`W` * **P**\ :sub:`H`

- Pack weight: TODO
