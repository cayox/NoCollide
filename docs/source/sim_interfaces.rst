.. index:: Simulation Integration

======================
Simulation Integration
======================
To establish a neatless simulation, the code that is intended to use hardware must be extended/changed to use the simulation's
sensors. That's why simulation classes are needed, to adapt to the challanges of merging different usecases in one API.

.. autoclass:: lib.sim_interfaces.SimNoCollide
   :members:

.. autoclass:: lib.sim_interfaces.SimSensor
   :members:

.. autoclass:: lib.sim_interfaces.SimSensorGroup
   :members:
