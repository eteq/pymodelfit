#Copyright 2009 Erik Tollerud
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
This module contains the internals for the FitGui gui.
"""
#TODO: change single select to click-to-do-action 

from __future__ import division,with_statement
import numpy as np

from enthought.traits.api import HasTraits,Bool,Button,Float,Int,Color, \
                                 Instance,Tuple,Array,List,Dict,Str,Property, \
                                on_trait_change,cached_property
from enthought.traits.ui.api import View,VGroup,HGroup,Item,TupleEditor, \
                                    ListEditor



from .fitgui import FitGui,TraitedModel
from enthought.tvtk.pyface.scene_editor import SceneEditor 
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene
        
class MultiFitGui(HasTraits):
    """
    data should be c x N where c is the number of data columns/axes and N is 
    the number of points
    """
    doplot3d = Bool(False)
    show3d = Button('Show 3D Plot')
    replot3d = Button('Replot 3D')
    scalefactor3d = Float(0)
    do3dscale = Bool(False)
    nmodel3d = Int(1024)
    usecolor3d = Bool(False)
    color3d = Color((0,0,0))
    scene3d = Instance(MlabSceneModel,())
    plot3daxes = Tuple(('x','y','z'))
    data = Array(shape=(None,None))
    weights = Array(shape=(None,))
    curveaxes = List(Tuple(Int,Int))
    axisnames = Dict(Int,Str)
    invaxisnames = Property(Dict,depends_on='axisnames')
    
    fgs = List(Instance(FitGui))
    
    
    traits_view = View(VGroup(Item('fgs',editor=ListEditor(use_notebook=True,page_name='.plotname'),style='custom',show_label=False),
                              Item('show3d',show_label=False)),
                              resizable=True,height=900,buttons=['OK','Cancel'],title='Multiple Model Data Fitters')
                              
    plot3d_view = View(VGroup(Item('scene3d',editor=SceneEditor(scene_class=MayaviScene),show_label=False,resizable=True),
                              Item('plot3daxes',editor=TupleEditor(cols=3,labels=['x','y','z']),label='Axes'),
                              HGroup(Item('do3dscale',label='Scale by weight?'),
                              Item('scalefactor3d',label='Point scale'),
                              Item('nmodel3d',label='Nmodel')),
                              HGroup(Item('usecolor3d',label='Use color?'),Item('color3d',label='Relation Color',enabled_when='usecolor3d')),
                              Item('replot3d',show_label=False),springy=True),
                       resizable=True,height=800,width=800,title='Multiple Model3D Plot')
    
    def __init__(self,data,names=None,models=None,weights=None,dofits=True,**traits):
        """
        :param data: The data arrays 
        :type data: sequence of c equal-length arrays (length N)
        :param names: Names 
        :type names: sequence of strings, length c
        :param models: 
            The models to fit for each pair either as strings or
            :class:`astroypsics.models.ParametricModel` objects.
        :type models: sequence of models, length c-1
        :param weights: the weights for each point or None for no weights
        :type weights: array-like of size N or None
        :param dofits: 
            If True, the data will be fit to the models when the object is 
            created, otherwise the models will be passed in as-is (or as
            created).
        :type dofits: bool 
        
        extra keyword arguments get passed in as new traits
        (r[finmask],m[finmask],l[finmask]),names='rh,Mh,Lh',weights=w[finmask],models=models,dofits=False)
        """
        super(MultiFitGui,self).__init__(**traits)
        self._lastcurveaxes = None
        
        data = np.array(data,copy=False)
        if weights is None:
            self.weights = np.ones(data.shape[1])
        else:
            self.weights = np.array(weights)
        
        self.data = data
        if data.shape[0] < 2:
            raise ValueError('Must have at least 2 columns')
        
        if isinstance(names,basestring):
            names = names.split(',')
        if names is None:
            if len(data) == 2:
                self.axisnames = {0:'x',1:'y'}
            elif len(data) == 3:
                self.axisnames = {0:'x',1:'y',2:'z'}
            else:
                self.axisnames = dict((i,str(i)) for i in data)
        elif len(names) == len(data):
            self.axisnames = dict([t for t in enumerate(names)])
        else:
            raise ValueError("names don't match data")
        
        #default to using 0th axis as parametric
        self.curveaxes = [(0,i) for i in range(len(data))[1:]]
        if models is not None:
            if len(models) != len(data)-1:
                raise ValueError("models don't match data")
            for i,m in enumerate(models):
                fg = self.fgs[i]
                newtmodel = TraitedModel(m)
                if dofits:
                    fg.tmodel = newtmodel
                    fg.fitmodel = True #should happen automatically, but this makes sure
                else:
                    oldpard = newtmodel.model.pardict
                    fg.tmodel = newtmodel
                    fg.tmodel .model.pardict = oldpard
                if dofits:
                    fg.fitmodel = True
        
    def _data_changed(self):
        self.curveaxes = [(0,i) for i in range(len(self.data))[1:]]

    def _axisnames_changed(self):
        for ax,fg in zip(self.curveaxes,self.fgs):
            fg.plot.x_axis.title = self.axisnames[ax[0]] if ax[0] in self.axisnames else ''
            fg.plot.y_axis.title = self.axisnames[ax[1]] if ax[1] in self.axisnames else ''
        self.plot3daxes = (self.axisnames[0],self.axisnames[1],self.axisnames[2] if len(self.axisnames) > 2 else self.axisnames[1])
        
    @on_trait_change('curveaxes[]')
    def _curveaxes_update(self,names,old,new):
        ax=[]
        for t in self.curveaxes:
            ax.append(t[0])
            ax.append(t[1])
        if set(ax) != set(range(len(self.data))):
            self.curveaxes = self._lastcurveaxes
            return #TOOD:check for recursion
            
        if self._lastcurveaxes is None:
            self.fgs = [FitGui(self.data[t[0]],self.data[t[1]],weights=self.weights) for t in self.curveaxes]
            for ax,fg in zip(self.curveaxes,self.fgs):
                fg.plot.x_axis.title = self.axisnames[ax[0]] if ax[0] in self.axisnames else ''
                fg.plot.y_axis.title = self.axisnames[ax[1]] if ax[1] in self.axisnames else ''
        else:
            for i,t in enumerate(self.curveaxes):
                if  self._lastcurveaxes[i] != t:
                    self.fgs[i] = fg = FitGui(self.data[t[0]],self.data[t[1]],weights=self.weights)
                    ax = self.curveaxes[i]
                    fg.plot.x_axis.title = self.axisnames[ax[0]] if ax[0] in self.axisnames else ''
                    fg.plot.y_axis.title = self.axisnames[ax[1]] if ax[1] in self.axisnames else ''
        
        self._lastcurveaxes = self.curveaxes
        
    def _show3d_fired(self):
        self.edit_traits(view='plot3d_view')
        self.doplot3d = True
        self.replot3d = True
        
    def _plot3daxes_changed(self):
        self.replot3d = True
        
    @on_trait_change('weights',post_init=True)
    def weightsChanged(self):
        for fg in self.fgs:
            if fg.weighttype != 'custom':
                fg.weighttype = 'custom'
            fg.weights = self.weights
            
        
    @on_trait_change('data','fgs','replot3d','weights')
    def _do_3d(self):
        if self.doplot3d:
            M = self.scene3d.mlab
            try:
                xi = self.invaxisnames[self.plot3daxes[0]]
                yi = self.invaxisnames[self.plot3daxes[1]]
                zi = self.invaxisnames[self.plot3daxes[2]]
                
                x,y,z = self.data[xi],self.data[yi],self.data[zi]
                w = self.weights

                M.clf()
                if self.scalefactor3d == 0:
                    sf = x.max()-x.min()
                    sf *= y.max()-y.min()
                    sf *= z.max()-z.min()
                    sf = sf/len(x)/5
                    self.scalefactor3d = sf
                else:
                    sf = self.scalefactor3d
                glyph = M.points3d(x,y,z,w,scale_factor=sf)
                glyph.glyph.scale_mode = 0 if self.do3dscale else 1
                M.axes(xlabel=self.plot3daxes[0],ylabel=self.plot3daxes[1],zlabel=self.plot3daxes[2])
                
                try:
                    xs = np.linspace(np.min(x),np.max(x),self.nmodel3d)
                    
                    #find sequence of models to go from x to y and z
                    ymods,zmods = [],[]
                    for curri,mods in zip((yi,zi),(ymods,zmods)):
                        while curri != xi:
                            for i,(i1,i2) in enumerate(self.curveaxes):
                                if curri==i2:
                                    curri = i1
                                    mods.insert(0,self.fgs[i].tmodel.model)
                                    break
                            else:
                                raise KeyError
                    
                    ys = xs
                    for m in ymods:
                        ys = m(ys)
                    zs = xs
                    for m in zmods:
                        zs = m(zs)
                    
                    if self.usecolor3d:
                        c = (self.color3d[0]/255,self.color3d[1]/255,self.color3d[2]/255)
                        M.plot3d(xs,ys,zs,color=c)
                    else:
                        M.plot3d(xs,ys,zs,np.arange(len(xs)))
                except (KeyError,TypeError):
                    M.text(0.5,0.75,'Underivable relation')
            except KeyError:
                M.clf()
                M.text(0.25,0.25,'Data problem')
                
            
            
    @cached_property        
    def _get_invaxisnames(self):
        d={}
        for k,v in self.axisnames.iteritems():
            d[v] = k
        return d
    
def fit_data_multi(data,names=None,weights=None,models=None):
    """
    fit a data set consisting of a variety of curves simultaneously. A GUI 
    application instance must already exist (e.g. interactive mode of 
    ipython)    
    
    returns a tuple of models e.g. [xvsy,xvsz]
    """
    
    if len(data.shape) !=2 or data.shape[0]<2:
        raise ValueError('data must be 2D with first dimension >=2')
    
    if models is not None and len(models) != data.shape[0]:
        raise ValueError('Number of models does not match number of data sets')
    
    mfg = MultiFitGui(data,names,models,weights=weights)

    res = mfg.edit_traits(kind='livemodal')

    if res:
        return tuple([fg.tmodel.model for fg in mfg.fgs])
    else:
        return None
