#Copyright 2008 Erik Tollerud
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Internal utility functions used in pymodelfit - most of these are lifted from
:mod:`astropysics` for a few specific purposes
"""

from contextlib import contextmanager

#all of these are CGS
me = 9.1093897e-28 #electron mass
kb = 1.3807e-16 #boltzmann's constant
c = 2.99792458e10 #speed of light - exact

_mpl_show_default = False
@contextmanager
def mpl_context(show=None,clf=False,savefn=None):
    """
    Used for with statements containing matplotlib plots.  Usage::
    
        with _mpl_context() as plt:
            plt.plot(x,y,...)
            plt.scatter(xs,ys,...)
        
    :param bool show: 
        If True,:func:`pyplot.show` will be called when plotting is completed.
        This blocks execution until the user closes the plotting window.
    :param bool clf: If True, the figure will be cleared before plotting.
    :param savefn: 
        A string to save the figure to via the :func:`matplotlib.pyplot.savefig`
        function, or None to not save the figure.
    """
    if show is None:
        show = _mpl_show_default
    
    isinter = plt.isinteractive()
    try:
        if isinter:
            #TODO: figure out why this is necessary (probably an mpl/ipython problem)
            plt.gcf()
        plt.interactive(False)
        if clf:
            plt.clf()
            
        yield plt
        
    finally:
        plt.interactive(isinter)
        
    if savefn:
        plt.savefig(savefn)
    if show:
        plt.draw()
        plt.show()
    else:
        plt.draw_if_interactive()
        
        
def cartesian_to_polar(x,y,degrees=False):
    """
    Converts arrays in 2D rectangular Cartesian coordinates to polar
    coordinates.
    
    :param x: First cartesian coordinate
    :type x: :class:`numpy.ndarray`
    :param y: Second cartesian coordinate
    :type y: :class:`numpy.ndarray`
    :param degrees: 
        If True, the output theta angle will be in degrees, otherwise radians.
    :type degrees: boolean
    
    :returns: 
        (r,theta) where theta is measured from the +x axis increasing towards
        the +y axis
    """
    r = (x*x+y*y)**0.5
    t = np.arctan2(y,x)
    if degrees:
        t = np.degrees(t)
    
    return r,t

def polar_to_cartesian(r,t,degrees=False):
    """
    Converts arrays in 2D polar coordinates to rectangular cartesian
    coordinates.
    
    Note that the spherical coordinates are in *physicist* convention such that
    (1,0,pi/2) is x-axis.
    
    :param r: Radial coordinate
    :type r: :class:`numpy.ndarray`
    :param t: Azimuthal angle from +x-axis increasing towards +y-axis
    :type t: :class:`numpy.ndarray`
    :param degrees: 
        If True, the input angles will be in degrees, otherwise radians.
    :type degrees: boolean
    
    :returns: arrays (x,y)
    """
    if degrees:
        t=np.radians(t)
        
    return r*np.cos(t),r*np.sin(t)