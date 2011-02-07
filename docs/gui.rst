
Fitgui -- Interactive Curve Fitting
===================================

This module contains the interactive GUI curve-fitting tools. They are based on
`Traits <http://code.enthought.com/projects/traits/>`_ and `TraitsGUI
<http://code.enthought.com/projects/traits_gui/>`_. Plotting is provided through
the `Chaco <http://code.enthought.com/projects/chaco/>`_ 2D plotting library ,
and, optionally, `Mayavi <http://code.enthought.com/projects/mayavi/>`_ for 3D
plotting. The available models are those registered by the
:func:`pymodelmit.core.register_model` mechanism.


FitGui -- Interactive 1D model-fitting
--------------------------------------

Reference
^^^^^^^^^

.. autoclass:: pymodelfit.fitgui.FitGui
   :members:
   :undoc-members:
   :exclude-members: modelpanel,modelselector
   
.. autofunction:: pymodelfit.fitgui.fit_data


MultiFitGui -- Interactive fitting for multiple 1D models
---------------------------------------------------------

Note that the MultiFitGui requires Mayavi due to the need for 3D plotting.

Reference
^^^^^^^^^

.. autoclass:: pymodelfit.multifitgui.MultiFitGui
   :members:
   :undoc-members:
   :exclude-members: modelpanel,modelselector


.. autofunction:: pymodelfit.multifitgui.fit_data_multi