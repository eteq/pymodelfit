#!/usr/bin/env python
#Copyright (c) 2011 Erik Tollerud (erik.tollerud@gmail.com) 
from __future__ import division,with_statement

from glob import glob
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup,find_packages
from distutils.command.build_py import build_py as du_build_py

from pymodelfit import version as versionstr
    
descrip = """
`pymodelfit` is a pythonic, object-oriented framework and GUI tool for fitting data to models.
      
See http://packages.python.org/PyModelFit/ for detailed documentation.
"""
        
        
#custom sphinx builder just makes the directory to build if it hasn't already been made
try:
    from sphinx.setup_command import BuildDoc
    
    class mod_build_sphinx(BuildDoc):
        def finalize_options(self):
            from os.path import isfile    
            from distutils.cmd import DistutilsOptionError
            
            if self.build_dir is not None:
                if isfile(self.build_dir):
                    raise DistutilsOptionError('Attempted to build_sphinx into a file '+self.build_dir)
                self.mkpath(self.build_dir)
            return BuildDoc.finalize_options(self)
            
except ImportError: #sphinx not present
    mod_build_sphinx = None
    
cmdclassd = {}
if mod_build_sphinx is not None:
    cmdclassd['build_sphinx'] = mod_build_sphinx
    
setup(name='PyModelFit',
      version=versionstr,
      description='Data-fitting and Model-building package',
      packages=find_packages(),
      scripts=glob('scripts/*'),
      requires=['numpy','scipy'],
      install_requires=['numpy'],
      provides=['pymodelfit'],
      extras_require={'all':'traits,traitsgui,chaco,matplotlib'.split(',')},  
      author='Erik Tollerud',
      author_email='erik.tollerud@gmail.com',
      license = 'Apache License 2.0',
      url='http:http://packages.python.org/PyModelFit/',
      long_description=descrip,
      cmdclass = cmdclassd
     )
