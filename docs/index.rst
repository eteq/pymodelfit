.. PyModelFit documentation master file, created by
   sphinx-quickstart on Mon Jan 31 02:23:52 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyModelFit: model-fitting framework and GUI tool
================================================
:Author: `Erik Tollerud <http://www.physics.uci.edu/~etolleru/>`_

PyModelFit is a package that provides a pythonic, object-oriented framework 
that simplifies the task of designing numerical models to fit data.  This
is a very broad task, and hence the current functionality of PyModelFit focuses
on the simpler tasks of 1D curve-fitting, including a GUI interface to simplify
interactive work (using Enthought Traits). For more complicated modeling, 
PyModelFit also provides a wide range of classes and a framework to support 
more general model/data types (2D to Scalar, 3D to Scalar, 3D to 3D, and so 
on).

.. note ::
    This project is a spin off of 
    `Astropysics <http://packages.python.org/Astropysics/>`_, although it 
    doesn't require astropysics.

Contents:

.. toctree::
   :maxdepth: 3
   
   start
   over
   gui
   core
   builtins
   
   
Quick Install
=============

See :doc:`start` for full install instructions.

To install the current release of pymodelfit, the simplest approach is::

    pip install pymodelfit

(on unix-like systems or OS X, add "sudo " before this command)

Note that you must have `numpy <http://numpy.scipy.org>`_ and 
`scipy <http://www.scipy.org/>`_ installed, although the installer should 
install them for you if they are not already present.  To use the FitGUI, you 
will need `Traits <http://code.enthought.com/projects/traits/>`_, 
`TraitsGUI <http://code.enthought.com/projects/traits_gui/>`_, and 
`Chaco <http://code.enthought.com/projects/chaco/>`_.

       
Bug Reports
===========

Please report any bugs encountered to the 
`github issue tracker <http://github.com/eteq/pymodelfit/issues>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

