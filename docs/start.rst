Getting Started with PyModelFit
===============================


Requirements
------------
Before you do anything with PyModelFit, you'll need:

    * `Python <http://www.python.org/>`_ 2.5 or higher (2.6 highly recommended), although 3.x is not yet supported.
    * `numpy <http://numpy.scipy.org>`_ 
    * `scipy <http://www.scipy.org/>`_
    
Follow the instructions on those sites, or, far easier, install them as packages from your operating system (e.g. apt-get or the synaptic GUI on Ubuntu, `Macports <http://www.macports.org/>`_ on OS X, etc.).  


Install
-------

Once you have the requirements satisfied, you have a few options for installing astropysics.  

.. note::
    On most unix-like systems, you will need to either execute these commands as the root user, or preface them with ``sudo``.

If you have `pip <http://pypi.python.org/pypi/pip>`_ (the new, better easy installer) or `easy_install/setuptools <http://pypi.python.org/pypi/setuptools>`_ (you should probably install pip...), just run either::

    pip install pymodelfit

or::

    easy_install pymodelfit

If you are installing from source code, instead, just do::

    python setup.py install


Additional Recommended Packages
-------------------------------

A few other outside packages add useful functionality to PyModelFit.  These
are not required, but are highly recommended for the full PyModelFit 
experience.  

For general publication-quality plotting of data and models, the
following package is suggested:

    * `Matplotlib <http://matplotlib.sourceforge.net/index.html>`_
        Can be installed with ``pip install matplotlib``
    
To use the useful FitGUI interactive model-fitting tool, the following three
packages are necessary (with the suggested install command, if you don't
have the package already available on your system):

    * `Traits <http://code.enthought.com/projects/traits/>`_
        ``pip install traits``
    * `TraitsGUI <http://code.enthought.com/projects/traits_gui/>`_
        ``pip install traitsGUI``
    * `Chaco <http://code.enthought.com/projects/chaco/>`_
        ``pip install chaco``

