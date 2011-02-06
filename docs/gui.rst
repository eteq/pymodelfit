
Fitgui -- Interactive Curve Fitting
===================================

This module contains the interactive GUI curve-fitting tools. They are based on
`Traits <http://code.enthought.com/projects/traits/>`_ and the `TraitsGUI
<http://code.enthought.com/projects/traits_gui/>`. Plotting is provided through
the `Chaco <http://code.enthought.com/projects/chaco/>`_ 2D plotting library ,
and, optionally, `Mayavi <http://code.enthought.com/projects/mayavi/>`_ for 3D
plotting. The available models are those registered by the
:func:`pymodelmit.core.register_model` mechanism.


FitGui -- Interactive 1D model-fitting
--------------------------------------

.. autoclass:: pymodelfit.fitgui.FitGui
   :members:
   :undoc-members:
   :exclude-members: modelpanel,modelselector
   
.. autofunction:: pymodelfit.fitgui.fit_data


MultiFitGui -- Interactive fitting for multiple 1D models
---------------------------------------------------------

Note that the MultiFitGui requires Mayavi for 3D plotting

.. autoclass:: pymodelfit.fitgui.MultiFitGui
   :members:
   :undoc-members:
   :exclude-members: modelpanel,modelselector


.. autofunction:: pymodelfit.fitgui.fit_data_multi