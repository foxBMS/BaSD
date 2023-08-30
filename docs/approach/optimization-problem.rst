.. include:: ./../macros.txt

.. _OPTIMIZATION_PROBLEM:

####################
Optimization Problem
####################


Defining the optimization problem:

.. math::

    min: & P_V \\
    & P_N P_R P_L C_N C_R Cell_{Capacity} \geq R_C \\
    & S_N S_R S_L M_N M_R Cell_{Voltage} \geq R_V \\
    & M_N M_R Cell_{Voltage} \leq 60 V \\
    & P_W < R_W \\
    & P_L < R_L \\
    & P_H < R_H \\
    & P_R, P_N, P_S, P_M, P_C \in \mathbb{N} \\

with :math:`R_C, R_V` as required system capacity and voltage,
:math:`R_W, R_L, R_H` as maximal system width, length and height.
