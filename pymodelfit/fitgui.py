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

from enthought.traits.api import HasTraits,Instance,Int,Float,Bool,Button, \
                                 Event,Property,on_trait_change,Array,List, \
                                 Tuple,Str,Dict,cached_property,Color,Enum, \
                                 TraitError,Undefined,DelegatesTo
from enthought.traits.ui.api import View,Handler,Item,Label,Group,VGroup, \
                                    HGroup, InstanceEditor,EnumEditor, \
                                    ListEditor, TupleEditor,spring
from enthought.traits.ui.menu import ModalButtons
from enthought.chaco.api import Plot,ArrayPlotData,jet,ColorBar,HPlotContainer,\
                                ColorMapper,LinearMapper,ScatterInspectorOverlay,\
                                LassoOverlay,AbstractOverlay,ErrorBarPlot, \
                                ArrayDataSource
from enthought.chaco.tools.api import PanTool,SelectTool,LassoSelection,ScatterInspector
from enthought.enable.api import ColorTrait,ComponentEditor
from enthought.enable.base_tool import KeySpec
try:
    #I'm not certain when BetterSelectingZoom was implemented...
    from enthought.chaco.tools.api import BetterSelectingZoom as ZoomTool
except ImportError:
    from enthought.chaco.tools.api import ZoomTool




from .core import FunctionModel1D,list_models,get_model_class,get_model_instance
from .utils import binned_weights

class ColorMapperFixSingleVal(ColorMapper):
    coloratval = ColorTrait('black')
    val = 0
    
    def map_screen(self, data_array):
        res = super(ColorMapperFixSingleVal,self).map_screen(data_array)
        res[data_array==self.val] = self.coloratval_
        return res

#_cmap = jet
def _cmapblack(range, **traits):
    _data =   {'red':   ((0,1,1), (0.3, .8, .8), (0.5, 0, 0), (0.75,0.75, 0.75),(.875,.2,.2),
                         (1, 0, 0)),
               'blue': ((0., 0, 0), (0.3,0, 0), (0.5,0, 0), (0.75,.75, .75),
                         (0.875,0.75,0.75), (1, 1, 1)),
               'green':  ((0.,0, 0),(0.3,.8,.8), (0.4, 0.4, 0.4),(0.5,1,1), (0.65,.75, .75), (0.75,0.1, 0.1),
                         (1, 0, 0))}

    return ColorMapperFixSingleVal.from_segment_map(_data, range=range, **traits)

def _cmap(range, **traits):
    _data =   {'red':   ((0,1,1), (0.3, .8, .8), (0.5, 0, 0), (0.75,0.75, 0.75),(.875,.2,.2),
                         (1, 0, 0)),
               'blue': ((0., 0, 0), (0.3,0, 0), (0.5,0, 0), (0.75,.75, .75),
                         (0.875,0.75,0.75), (1, 1, 1)),
               'green':  ((0.,0, 0),(0.3,.8,.8), (0.4, 0.4, 0.4),(0.5,1,1), (0.65,.75, .75), (0.75,0.1, 0.1),
                         (1, 0, 0))}

#    """ inverted version of 'jet' colormap"""

#    _data =   {'red':   ((0., 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89,1, 1),
#                         (1, 0.5, 0.5)),
#               'green': ((0., 0, 0), (0.125,0, 0), (0.375,1, 1), (0.64,1, 1),
#                         (0.91,0,0), (1, 0, 0)),
#               'blue':  ((0., 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1), (0.65,0, 0),
#                         (1, 0, 0))}
#    for k,v in _data.items():
#        _data[k] = tuple(reversed([(v[-1-i][0],t[1],t[2]) for i,t in enumerate(v)]))
#    
    return ColorMapper.from_segment_map(_data, range=range, **traits)

class TraitedModel(HasTraits):
    from inspect import isclass
    
    model = Instance(FunctionModel1D,allow_none=True)
    modelname = Property(Str)
    updatetraitparams = Event
    paramchange = Event
    fitdata = Event
    fittype = Property(Str)
    fittypes = Property
    lastfitfailure = Instance(Exception,allow_none=True)
    
    def __init__(self,model,**traits):
        super(TraitedModel,self).__init__(**traits)
        
        from inspect import isclass
        
        if isinstance(model,basestring):
            model = get_model_instance(model)
        elif isclass(model):
            model = model()
        self.model = model
        
    def default_traits_view(self):
        if self.model is None:
            g = Group()
            g.content.append(Label('No Model Selected'))
        else:
            #g = Group(label=self.modelname,show_border=False,orientation='horizontal',layout='flow')
            g = Group(label=self.modelname,show_border=True,orientation='vertical')
            hg = HGroup(Item('fittype',label='Fit Technique',
                             editor=EnumEditor(name='fittypes')))
            g.content.append(hg)
            gp = HGroup(scrollable=True)
            for p in self.model.params:
                gi = Group(orientation='horizontal',label=p)
                self.add_trait(p,Float)
                setattr(self,p,getattr(self.model,p))
                self.on_trait_change(self._param_change_handler,p)
                gi.content.append(Item(p,show_label=False))
                
                ffp = 'fixfit_'+p
                self.add_trait(ffp,Bool)
                #default to fixed if the paramtere is a class-level fixed model
                setattr(self,ffp,p in self.model.__class__.fixedpars)
                self.on_trait_change(self._param_change_handler,ffp)
                gi.content.append(Item(ffp,label='Fix?'))
                
                gp.content.append(gi)
            g.content.append(gp)
            
        return View(g,buttons=['Apply','Revert','OK','Cancel'])
    
    def _param_change_handler(self,name,new):
        setattr(self.model,name,new)
        self.paramchange = name
    
    def _updatetraitparams_fired(self):
        m = self.model
        for p in m.params:
            setattr(self,p,getattr(m,p))
        self.paramchange = True
        
    def _fitdata_fired(self,new):
        from operator import isSequenceType,isMappingType
        
        if self.model is not None:
            if isSequenceType(new) and len(new) == 2:
                kw={'x':new[0],'y':new[1]}
            elif isSequenceType(new) and len(new) == 3:
                kw={'x':new[0],'y':new[1],'weights':new[2]}
            elif isMappingType(new):
                kw = dict(new)
                
                #add any missing pieces
                for i,k in enumerate(('x','y','weights')):
                    if k not in new:
                        if self.model.fiteddata:
                            new[k] = self.model.fiteddata[i]
                        else:
                            raise ValueError('no pre-fitted data available')
            elif new is True:
                if self.model.fiteddata:
                    fd = self.model.fiteddata
                    kw= {'x':fd[0],'y':fd[1],'weights':fd[2]}
                else:
                    raise ValueError('No data to fit')
            else:
                raise ValueError('unusable fitdata event input')
            
            if 'fixedpars' not in kw:
                 kw['fixedpars'] = [tn.replace('fixfit_','') for tn in self.traits() if tn.startswith('fixfit_') if getattr(self,tn)]
            try:
                self.model.fitData(**kw)
                self.updatetraitparams = True
                self.lastfitfailure = None
            except Exception,e:
                self.lastfitfailure = e
    
    def _get_modelname(self):
        if self.model is None:
            return 'None'
        else:
            return self.model.__class__.__name__
    
    def _get_fittype(self):
        if self.model is None:
            return None
        else:
            return self.model.fittype
        
    def _set_fittype(self,val):
        self.model.fittype = val
        
    def _get_fittypes(self):
        return self.model.fittypes
        
class NewModelSelector(HasTraits):
    modelnames = List
    selectedname = Str('No Model')
    modelargnum = Int(2)
    selectedmodelclass = Property
    isvarargmodel = Property(depends_on='modelnames')
    
    traits_view = View(Item('selectedname',label='Model Name:',editor=EnumEditor(name='modelnames')),
                       Item('modelargnum',label='Extra Parameters:',enabled_when='isvarargmodel'),
                       buttons=['OK','Cancel'])
    
    def __init__(self,include_models=None,exclude_models=None,**traits):
        super(NewModelSelector,self).__init__(**traits)
        
        self.modelnames = list_models(include_models,exclude_models,FunctionModel1D)
        self.modelnames.insert(0,'No Model')
        self.modelnames.sort()
        
    def _get_selectedmodelclass(self):
        n = self.selectedname
        if n == 'No Model':
            return None
        else:
            return get_model_class(n)
        
    def _get_isvarargmodel(self):
        cls = self.selectedmodelclass
        
        if cls is None:
            return False
        else:
            return cls.isVarnumModel()
        
#class WeightFillOverlay(AbstractOverlay):
#    weightval = Float(0)
#    color = ColorTrait('black')
#    plot = Instance(Plot)
    
#    def overlay(self, component, gc, view_bounds=None, mode="normal"):
#        from enthought.chaco.scatterplot import render_markers
        
#        plot = self.component
#        scatter = plot.plots['data'][0]
#        if not plot or not scatter or not scatter.index or not scatter.value:
#            return
        
#        w = plot.data.get_data('weights')
#        inds = w==self.weightval
        
#        index_data = scatter.index.get_data()
#        value_data = scatter.value.get_data()
#        screen_pts = scatter.map_screen(np.array([index_data[inds],value_data[inds]]).T)
#        screen_pts = screen_pts+[plot.x,plot.y]
        
#        props = ('line_width','marker_size','marker')
#        markerprops = dict([(prop,getattr(scatter,prop)) for prop in props])
        
#        markerprops['color']=self.color_
#        markerprops['outline_color']=self.color_
        
#        if markerprops.get('marker', None) == 'custom':
#            markerprops['custom_symbol'] = scatter.custom_symbol
        
#        gc.save_state()
#        gc.clip_to_rect(scatter.x+plot.x, scatter.y+plot.y, scatter.width, scatter.height)
#        render_markers(gc, screen_pts, **markerprops)
#        gc.restore_state()

class FGHandler(Handler):
#    def object_selbutton_changed(self,info):
#        info.object.edit_traits(parent=info.ui.control,view='selection_view')
        
    def object_datasymb_changed(self,info):
        kind = info.ui.rebuild.__name__.replace('ui_','') #TODO:not hack!
        info.object.plot.plots['data'][0].edit_traits(parent=info.ui.control,
                                                      kind=kind)
    
    def object_modline_changed(self,info):
        kind = info.ui.rebuild.__name__.replace('ui_','') #TODO:not hack!
        info.object.plot.plots['model'][0].edit_traits(parent=info.ui.control,
                                                       kind=kind)
                                                       

class FitGui(HasTraits):
    """
    This class represents the fitgui application state.
    """
    
    plot = Instance(Plot)
    colorbar = Instance(ColorBar)
    plotcontainer = Instance(HPlotContainer)
    tmodel = Instance(TraitedModel,allow_none=False)
    nomodel = Property
    newmodel = Button('New Model...')
    fitmodel = Button('Fit Model')
    showerror = Button('Fit Error')
    updatemodelplot = Button('Update Model Plot')
    autoupdate = Bool(True)
    data = Array(dtype=float,shape=(2,None))
    weights = Array
    weighttype = Enum(('custom','equal','lin bins','log bins'))
    weightsvary = Property(Bool)
    weights0rem = Bool(True)
    modelselector = NewModelSelector
    ytype = Enum(('data and model','residuals'))
    
    zoomtool = Instance(ZoomTool)
    pantool = Instance(PanTool)
      
    scattertool = Enum(None,'clicktoggle','clicksingle','clickimmediate','lassoadd','lassoremove','lassoinvert')
    selectedi = Property #indecies of the selected objects
    weightchangesel = Button('Set Selection To')
    weightchangeto = Float(1.0)
    delsel = Button('Delete Selected')
    unselectonaction = Bool(True)
    clearsel = Button('Clear Selections')
    lastselaction = Str('None')
    
    datasymb = Button('Data Symbol...')
    modline = Button('Model Line...')
    
    savews = Button('Save Weights')
    loadws = Button('Load Weights')
    _savedws = Array
    
    plotname = Property
    updatestats = Event
    chi2 = Property(Float,depends_on='updatestats')
    chi2r = Property(Float,depends_on='updatestats')
    
    
    nmod = Int(1024)
    #modelpanel = View(Label('empty'),kind='subpanel',title='model editor') 
    modelpanel = View
    
    panel_view = View(VGroup(
                       Item('plot', editor=ComponentEditor(),show_label=False),
                       HGroup(Item('tmodel.modelname',show_label=False,style='readonly'),
                              Item('nmod',label='Number of model points'),
                              Item('updatemodelplot',show_label=False,enabled_when='not autoupdate'),
                              Item('autoupdate',label='Auto?'))
                      ),
                    title='Model Data Fitter'
                    )
                    
                    
    selection_view = View(Group(
                           Item('scattertool',label='Selection Mode',
                                 editor=EnumEditor(values={None:'1:No Selection',
                                                           'clicktoggle':'3:Toggle Select',
                                                           'clicksingle':'2:Single Select',
                                                           'clickimmediate':'7:Immediate',
                                                           'lassoadd':'4:Add with Lasso',
                                                           'lassoremove':'5:Remove with Lasso',
                                                           'lassoinvert':'6:Invert with Lasso'})),
                           Item('unselectonaction',label='Clear Selection on Action?'), 
                           Item('clearsel',show_label=False),
                           Item('weightchangesel',show_label=False),
                           Item('weightchangeto',label='Weight'),
                           Item('delsel',show_label=False)
                         ),title='Selection Options')
    
    traits_view = View(VGroup(
                        HGroup(Item('object.plot.index_scale',label='x-scaling',
                                    enabled_when='object.plot.index_mapper.range.low>0 or object.plot.index_scale=="log"'),
                              spring,
                              Item('ytype',label='y-data'),
                              Item('object.plot.value_scale',label='y-scaling',     
                                   enabled_when='object.plot.value_mapper.range.low>0 or object.plot.value_scale=="log"')
                              ),
                       Item('plotcontainer', editor=ComponentEditor(),show_label=False),
                       HGroup(VGroup(HGroup(Item('weighttype',label='Weights:'),
                                            Item('savews',show_label=False),
                                            Item('loadws',enabled_when='_savedws',show_label=False)),
                                Item('weights0rem',label='Remove 0-weight points for fit?'),
                                HGroup(Item('newmodel',show_label=False),
                                       Item('fitmodel',show_label=False),
                                       Item('showerror',show_label=False,enabled_when='tmodel.lastfitfailure'),
                                       VGroup(Item('chi2',label='Chi2:',style='readonly',format_str='%6.6g',visible_when='tmodel.model is not None'),
                                             Item('chi2r',label='reduced:',style='readonly',format_str='%6.6g',visible_when='tmodel.model is not None'))
                                       )#Item('selbutton',show_label=False))
                              ,springy=False),spring,
                              VGroup(HGroup(Item('autoupdate',label='Auto?'),
                              Item('updatemodelplot',show_label=False,enabled_when='not autoupdate')),
                              Item('nmod',label='Nmodel'),
                              HGroup(Item('datasymb',show_label=False),Item('modline',show_label=False)),springy=False),springy=True),
                       '_',       
                       HGroup(Item('scattertool',label='Selection Mode',
                                 editor=EnumEditor(values={None:'1:No Selection',
                                                           'clicktoggle':'3:Toggle Select',
                                                           'clicksingle':'2:Single Select',
                                                           'clickimmediate':'7:Immediate',
                                                           'lassoadd':'4:Add with Lasso',
                                                           'lassoremove':'5:Remove with Lasso',
                                                           'lassoinvert':'6:Invert with Lasso'})),
                           Item('unselectonaction',label='Clear Selection on Action?'), 
                           Item('clearsel',show_label=False),
                           Item('weightchangesel',show_label=False),
                           Item('weightchangeto',label='Weight'),
                           Item('delsel',show_label=False),
                         layout='flow'),
                       Item('tmodel',show_label=False,style='custom',editor=InstanceEditor(kind='subpanel'))
                      ),
                    handler=FGHandler(),
                    resizable=True, 
                    title='Data Fitting',
                    buttons=['OK','Cancel'],
                    width=700,
                    height=900
                    )
                    
    
    def __init__(self,xdata=None,ydata=None,weights=None,model=None,
                 include_models=None,exclude_models=None,fittype=None,**traits):
        """

        :param xdata: the first dimension of the data to be fit
        :type xdata: array-like
        :param ydata: the second dimension of the data to be fit
        :type ydata: array-like
        :param weights: 
            The weights to apply to the data. Statistically interpreted as inverse
            errors (*not* inverse variance). May be any of the following forms:
            
            * None for equal weights
            * an array of points that must match `ydata`
            * a 2-sequence of arrays (xierr,yierr) such that xierr matches the
              `xdata` and yierr matches `ydata`
            * a function called as f(params) that returns an array of weights 
              that match one of the above two conditions
        
        :param model: the initial model to use to fit this data
        :type model:
            None, string, or :class:`astropysics.models.core.FunctionModel1D`
            instance. 
        :param include_models: 
            With `exclude_models`, specifies which models should be available in
            the "new model" dialog (see `models.list_models` for syntax).
        :param exclude_models:
            With `include_models`, specifies which models should be available in
            the "new model" dialog (see `models.list_models` for syntax).
        :param fittype: 
            The fitting technique for the initial fit (see
            :class:`astropysics.models.core.FunctionModel`). 
        :type fittype: string
        
        kwargs are passed in as any additional traits to apply to the
        application.
        
        """

        self.modelpanel = View(Label('empty'),kind='subpanel',title='model editor')
        
        self.tmodel = TraitedModel(model)
        
        if model is not None and fittype is not None:
            self.tmodel.model.fittype = fittype
            
        if xdata is None or ydata is None:
            if not hasattr(self.tmodel.model,'data') or self.tmodel.model.data is None:
                raise ValueError('data not provided and no data in model')
            if xdata is None:
                xdata = self.tmodel.model.data[0]
            if ydata is None:
                ydata = self.tmodel.model.data[1]
            if weights is None:
                weights = self.tmodel.model.data[2]

        self.on_trait_change(self._paramsChanged,'tmodel.paramchange')
        
        self.modelselector = NewModelSelector(include_models,exclude_models)
        
        self.data = [xdata,ydata]
        
        
        if weights is None:
            self.weights = np.ones_like(xdata)
            self.weighttype = 'equal'
        else:
            self.weights = np.array(weights,copy=True)
            self.savews = True
            
        weights1d = self.weights
        while len(weights1d.shape)>1:
            weights1d = np.sum(weights1d**2,axis=0)
        
        pd = ArrayPlotData(xdata=self.data[0],ydata=self.data[1],weights=weights1d)
        self.plot = plot = Plot(pd,resizable='hv')
        
        self.scatter = plot.plot(('xdata','ydata','weights'),name='data',
                         color_mapper=_cmapblack if self.weights0rem else _cmap,
                         type='cmap_scatter', marker='circle')[0]
                         
        self.errorplots = None
                        
        if not isinstance(model,FunctionModel1D):
            self.fitmodel = True
            
        self.updatemodelplot = False #force plot update - generates xmod and ymod
        plot.plot(('xmod','ymod'),name='model',type='line',line_style='dash',color='black',line_width=2)
        del plot.x_mapper.range.sources[-1]  #remove the line plot from the x_mapper source so only the data is tied to the scaling
        
        self.on_trait_change(self._rangeChanged,'plot.index_mapper.range.updated')
        
        self.pantool = PanTool(plot,drag_button='left')
        plot.tools.append(self.pantool)
        self.zoomtool = ZoomTool(plot)
        self.zoomtool.prev_state_key = KeySpec('a')
        self.zoomtool.next_state_key = KeySpec('s')
        plot.overlays.append(self.zoomtool)
        
        self.scattertool = None
        self.scatter.overlays.append(ScatterInspectorOverlay(self.scatter, 
                        hover_color = "black",
                        selection_color="black",
                        selection_outline_color="red",
                        selection_line_width=2))
                        
        
        self.colorbar = colorbar = ColorBar(index_mapper=LinearMapper(range=plot.color_mapper.range),
                                            color_mapper=plot.color_mapper.range,
                                            plot=plot,
                                            orientation='v',
                                            resizable='v',
                                            width = 30,
                                            padding = 5)
        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom
        colorbar._axis.title = 'Weights'
        
        self.plotcontainer = container = HPlotContainer(use_backbuffer=True)
        container.add(plot)
        container.add(colorbar)
        
        super(FitGui,self).__init__(**traits)
        
        self.on_trait_change(self._scale_change,'plot.value_scale,plot.index_scale')
        
        if weights is not None and len(weights)==2:
            self.weightsChanged() #update error bars
        
    def _weights0rem_changed(self,old,new):
        if new:
            self.plot.color_mapper = _cmapblack(self.plot.color_mapper.range)
        else:
            self.plot.color_mapper = _cmap(self.plot.color_mapper.range)
        self.plot.request_redraw()
#        if old and self.filloverlay in self.plot.overlays:
#            self.plot.overlays.remove(self.filloverlay)
#        if new:
#            self.plot.overlays.append(self.filloverlay)
#        self.plot.request_redraw()
        
    def _paramsChanged(self):
        self.updatemodelplot = True
            
    def _nmod_changed(self):
        self.updatemodelplot = True
    
    def _rangeChanged(self):
        self.updatemodelplot = True
        
    #@on_trait_change('object.plot.value_scale,object.plot.index_scale',post_init=True)
    def _scale_change(self):
        self.plot.request_redraw()
    
    def _updatemodelplot_fired(self,new):
        #If the plot has not been generated yet, just skip the update
        if self.plot is None:
            return
        
        #if False (e.g. button click), update regardless, otherwise check for autoupdate
        if new and not self.autoupdate:
            return
        
        mod = self.tmodel.model
        if self.ytype == 'data and model':
            if mod:
                #xd = self.data[0]
                #xmod = np.linspace(np.min(xd),np.max(xd),self.nmod)
                xl = self.plot.index_range.low
                xh = self.plot.index_range.high
                if self.plot.index_scale=="log":
                    xmod = np.logspace(np.log10(xl),np.log10(xh),self.nmod)
                else:
                    xmod = np.linspace(xl,xh,self.nmod)
                ymod = self.tmodel.model(xmod)
                
                self.plot.data.set_data('xmod',xmod)
                self.plot.data.set_data('ymod',ymod)

            else:
                self.plot.data.set_data('xmod',[])
                self.plot.data.set_data('ymod',[])
        elif self.ytype == 'residuals':
            if mod:
                self.plot.data.set_data('xmod',[])
                self.plot.data.set_data('ymod',[])
                #residuals set the ydata instead of setting the model
                res = mod.residuals(*self.data)
                self.plot.data.set_data('ydata',res)
            else:
                self.ytype = 'data and model'
        else:
            assert True,'invalid Enum'
            
    
    def _fitmodel_fired(self):
        from warnings import warn
        
        preaup = self.autoupdate
        try:
            self.autoupdate = False
            xd,yd = self.data
            kwd = {'x':xd,'y':yd}
            if self.weights is not None:
                w = self.weights
                if self.weights0rem: 
                    if xd.shape == w.shape:
                        m = w!=0
                        w = w[m]
                        kwd['x'] = kwd['x'][m]
                        kwd['y'] = kwd['y'][m]
                    elif np.any(w==0):
                        warn("can't remove 0-weighted points if weights don't match data")
                kwd['weights'] = w
            self.tmodel.fitdata = kwd
        finally:
            self.autoupdate = preaup
            
        self.updatemodelplot = True
        self.updatestats = True
        
        
#    def _tmodel_changed(self,old,new):
#        #old is only None before it is initialized
#        if new is not None and old is not None and new.model is not None:
#            self.fitmodel = True
        
    def _newmodel_fired(self,newval):
        from inspect import isclass
        
        if isinstance(newval,basestring) or isinstance(newval,FunctionModel1D) \
           or (isclass(newval) and issubclass(newval,FunctionModel1D)):
            self.tmodel = TraitedModel(newval)
        else:
            if self.modelselector.edit_traits(kind='modal').result:
                cls = self.modelselector.selectedmodelclass
                if cls is None:
                    self.tmodel = TraitedModel(None)
                elif self.modelselector.isvarargmodel:
                    self.tmodel = TraitedModel(cls(self.modelselector.modelargnum))
                    self.fitmodel = True
                else:
                    self.tmodel = TraitedModel(cls())
                    self.fitmodel = True
            else: #cancelled
                return      
            
    def _showerror_fired(self,evt):
        if self.tmodel.lastfitfailure:
            ex = self.tmodel.lastfitfailure
            dialog = HasTraits(s=ex.__class__.__name__+': '+str(ex))
            view = View(Item('s',style='custom',show_label=False),
                        resizable=True,buttons=['OK'],title='Fitting error message')
            dialog.edit_traits(view=view)
            
    @cached_property
    def _get_chi2(self):
        try:
            return self.tmodel.model.chi2Data()[0]
        except:
            return 0
        
    @cached_property
    def _get_chi2r(self):
        try:
            return self.tmodel.model.chi2Data()[1]
        except:
            return 0
                
    def _get_nomodel(self):
        return self.tmodel.model is None
    
    def _get_weightsvary(self):
        w = self.weights
        return np.any(w!=w[0])if len(w)>0 else False
    
    def _get_plotname(self):
        xlabel = self.plot.x_axis.title
        ylabel = self.plot.y_axis.title
        if xlabel == '' and ylabel == '':
            return ''
        else:
            return xlabel+' vs '+ylabel
    def _set_plotname(self,val):
        if isinstance(val,basestring):
            val = val.split('vs')
            if len(val) ==1:
                val = val.split('-')
            val = [v.strip() for v in val]
        self.x_axis.title = val[0]
        self.y_axis.title = val[1]
    
    
    #selection-related
    def _scattertool_changed(self,old,new):
        if new == 'No Selection':
            self.plot.tools[0].drag_button='left' 
        else:
            self.plot.tools[0].drag_button='right' 
        if old is not None and 'lasso' in old:
            if new is not None and 'lasso' in new:
                #connect correct callbacks
                self.lassomode = new.replace('lasso','')
                return
            else:
                #TODO:test
                self.scatter.tools[-1].on_trait_change(self._lasso_handler,
                                            'selection_changed',remove=True) 
                del self.scatter.overlays[-1]
                del self.lassomode
        elif old == 'clickimmediate':
            self.scatter.index.on_trait_change(self._immediate_handler,
                                            'metadata_changed',remove=True)        
                
        self.scatter.tools = []    
        if new is None:
            pass
        elif 'click' in new:
            smodemap = {'clickimmediate':'single','clicksingle':'single',
                        'clicktoggle':'toggle'}
            self.scatter.tools.append(ScatterInspector(self.scatter,
                                      selection_mode=smodemap[new]))
            if new == 'clickimmediate':
                self.clearsel = True
                self.scatter.index.on_trait_change(self._immediate_handler,
                                                    'metadata_changed')
        elif 'lasso' in new:
            lasso_selection = LassoSelection(component=self.scatter,
                                    selection_datasource=self.scatter.index)
            self.scatter.tools.append(lasso_selection)
            lasso_overlay = LassoOverlay(lasso_selection=lasso_selection,
                                         component=self.scatter)
            self.scatter.overlays.append(lasso_overlay)
            self.lassomode = new.replace('lasso','')
            lasso_selection.on_trait_change(self._lasso_handler,
                                            'selection_changed')
            lasso_selection.on_trait_change(self._lasso_handler,
                                            'selection_completed')
            lasso_selection.on_trait_change(self._lasso_handler,
                                            'updated')
        else:
            raise TraitsError('invalid scattertool value')
        
    def _weightchangesel_fired(self):
        self.weights[self.selectedi] = self.weightchangeto
        if self.unselectonaction:
            self.clearsel = True
            
        self._sel_alter_weights()
        self.lastselaction = 'weightchangesel'
    
    def _delsel_fired(self):
        self.weights[self.selectedi] = 0
        if self.unselectonaction:
            self.clearsel = True
        
        self._sel_alter_weights()
        self.lastselaction = 'delsel'
        
    def _sel_alter_weights(self):
        if self.weighttype != 'custom':
            self._customweights = self.weights
            self.weighttype = 'custom'
        self.weightsChanged()
            
    def _clearsel_fired(self,event):
        if isinstance(event,list):
            self.scatter.index.metadata['selections'] = event
        else:
            self.scatter.index.metadata['selections'] = list()
        
    def _lasso_handler(self,name,new):
        if name == 'selection_changed':
            lassomask = self.scatter.index.metadata['selection'].astype(int)
            clickmask = np.zeros_like(lassomask)
            clickmask[self.scatter.index.metadata['selections']] = 1
            
            if self.lassomode == 'add':
                mask = clickmask | lassomask
            elif self.lassomode == 'remove':
                mask = clickmask & ~lassomask
            elif self.lassomode == 'invert':
                mask = np.logical_xor(clickmask,lassomask)
            else:
                raise TraitsError('lassomode is in invalid state')
            
            self.scatter.index.metadata['selections'] = list(np.where(mask)[0])
        elif name == 'selection_completed':
            self.scatter.overlays[-1].visible = False
        elif name == 'updated':
            self.scatter.overlays[-1].visible = True
        else:
            raise ValueError('traits event name %s invalid'%name)
        
    def _immediate_handler(self):
        sel = self.selectedi
        if len(sel) > 1:
            self.clearsel = True
            raise TraitsError('selection error in immediate mode - more than 1 selection')
        elif len(sel)==1:
            if self.lastselaction != 'None':
                setattr(self,self.lastselaction,True)
            del sel[0]
            
    def _savews_fired(self):
        self._savedws = self.weights.copy()
    
    def _loadws_fired(self):
        self.weights = self._savedws
        self._savews_fired()
            
    def _get_selectedi(self):
        return self.scatter.index.metadata['selections']
    
    
    @on_trait_change('data,ytype',post_init=True)
    def dataChanged(self):
        """
        Updates the application state if the fit data are altered - the GUI will
        know if you give it a new data array, but not if the data is changed
        in-place.
        """        
        pd = self.plot.data
        #TODO:make set_data apply to both simultaneously?
        pd.set_data('xdata',self.data[0])
        pd.set_data('ydata',self.data[1])
        
        self.updatemodelplot = False
        
    @on_trait_change('weights',post_init=True)    
    def weightsChanged(self):
        """
        Updates the application state if the weights/error bars for this model
        are changed - the GUI will automatically do this if you give it a new
        set of weights array, but not if they are changed in-place.
        """       
        weights = self.weights
        if 'errorplots' in self.trait_names():
            #TODO:switch this to updating error bar data/visibility changing
            if self.errorplots is not None:
                self.plot.remove(self.errorplots[0])
                self.plot.remove(self.errorplots[1])
                self.errorbarplots = None
                
            if len(weights.shape)==2 and weights.shape[0]==2:
                xerr,yerr = 1/weights
                
                high = ArrayDataSource(self.scatter.index.get_data()+xerr)
                low = ArrayDataSource(self.scatter.index.get_data()-xerr)
                ebpx = ErrorBarPlot(orientation='v',
                                   value_high = high,
                                   value_low = low,
                                   index = self.scatter.value,
                                   value = self.scatter.index,
                                   index_mapper = self.scatter.value_mapper,
                                   value_mapper = self.scatter.index_mapper
                                )
                self.plot.add(ebpx)
                
                high = ArrayDataSource(self.scatter.value.get_data()+yerr)
                low = ArrayDataSource(self.scatter.value.get_data()-yerr)
                ebpy = ErrorBarPlot(value_high = high,
                                   value_low = low,
                                   index = self.scatter.index,
                                   value = self.scatter.value,
                                   index_mapper = self.scatter.index_mapper,
                                   value_mapper = self.scatter.value_mapper
                                )
                self.plot.add(ebpy)
                
                self.errorplots = (ebpx,ebpy)

        while len(weights.shape)>1:
            weights = np.sum(weights**2,axis=0)
        self.plot.data.set_data('weights',weights)
        self.plot.plots['data'][0].color_mapper.range.refresh()
        
        if self.weightsvary:
            if self.colorbar not in self.plotcontainer.components:
                self.plotcontainer.add(self.colorbar)
                self.plotcontainer.request_redraw()
        elif self.colorbar in self.plotcontainer.components:
                self.plotcontainer.remove(self.colorbar)
                self.plotcontainer.request_redraw()
            
    
    def _weighttype_changed(self, name, old, new):
        if old == 'custom':
            self._customweights = self.weights
        
        if new == 'custom':
            self.weights = self._customweights #if hasattr(self,'_customweights') else np.ones_like(self.data[0])
        elif new == 'equal':
            self.weights = np.ones_like(self.data[0])
        elif new == 'lin bins':
            self.weights = binned_weights(self.data[0],10,False)
        elif new == 'log bins':
            self.weights = binned_weights(self.data[0],10,True)
        else:
            raise TraitError('Invalid Enum value on weighttype')
        
    def getModelInitStr(self):
        """
        Generates a python code string that can be used to generate a model with
        parameters matching the model in this :class:`FitGui`.
        
        :returns: initializer string
        
        """
        mod = self.tmodel.model
        if mod is None:
            return 'None'
        else:
            parstrs = []
            for p,v in mod.pardict.iteritems():
                parstrs.append(p+'='+str(v))
            if mod.__class__._pars is None: #varargs need to have the first argument give the right number
                varcount = len(mod.params)-len(mod.__class__._statargs)
                parstrs.insert(0,str(varcount))
            return '%s(%s)'%(mod.__class__.__name__,','.join(parstrs))
    
    def getModelObject(self):
        """
        Gets the underlying object representing the model for this fit.
        
        :returns: The :class:`astropysics.models.core.FunctionModel1D` object.
        """
        return self.tmodel.model
    
            
def fit_data(*args,**kwargs):
    """
    Fit a 2d data set using the :class:`FitGui` interface. A GUI application
    instance must already exist (e.g. interactive mode of ipython). This
    function is modal and will block until the user hits "OK" or "Cancel" - if 
    non-blocking behavior is desired, create a  :class:`FitGui` object and call
    :meth:`FitGui.edit_traits`.
    
    The following forms for input arguments are accepted:
    
    * fit_data(xdata,ydata)
    * fit_data(xdata,ydata,model)
    * fit_data(model)
        This form requires a :class:`FunctionModel1D` object that includes data
    
    :param xdata: the first dimension of the data to be fit
    :type xdata: array-like
    :param ydata: the second dimension of the data to be fit
    :type ydata: array-like
    :param model: the initial model to use to fit this data
    :type model: 
        None, string, or :class:`astropysics.models.core.FunctionModel1D`
        instance
        
    kwargs are passed into the fitgui initializer
    
    :returns: 
        The model or None if fitting is cancelled or no model is assigned in the
        GUI.
        
    **Examples**
        
    >>> from numpy.random import randn
    >>> fit_data(randn(100),randn(100)) #doctest: +SKIP 
    
    This will bring up 100 normally-distributed points with no initial fitting
    model.
    
    >>> from numpy.random import randn
    >>> fit_data(randn(100),randn(100),'linear') #doctest: +SKIP
    
    This will bring up 100 normally-distributed points with a best-fit linear
    model.
    
    >>> from numpy.random import randn
    >>> fit_data(randn(100),randn(100),'linear',weights=rand(100)) #doctest: +SKIP
    
    This will bring up 100 normally-distributed points with a best-fit linear
    model with the points weighted by uniform random values.
    
    >>> from numpy import tile
    >>> from numpy.random import randn,rand
    >>> fit_data(randn(100),randn(100),'linear',weights=tile(rand(100),2).reshape((2,10)),fittype='yerr') #doctest: +SKIP
    
    This will bring up 100 normally-distributed points with a linear model with
    the points weighted by a uniform random number (interpreted as inverse
    error) fit using the yerr algorithm instead of the default least-squares.
    
    """
    kwargs = dict(kwargs) #copy
    if len(args) == 2:
        xdata = args[0]
        ydata = args[1]
        kwargs.setdefault('model',None)
    elif len(args) == 3:
        xdata = args[0]
        ydata = args[1]
        if 'model' in kwargs:
            raise TypeError("got two values for 'model' argument")
        kwargs['model'] = args[2]
    elif len(args) == 1:
        xdata = ydata = None
        if 'model' in kwargs:
            raise TypeError("got two values for 'model' argument")
        kwargs['model'] = args[0]
        if kwargs['model'].data is None:
            raise ValueError('cannot fit_data for a model with no data')
    else:
        raise TypeError('fit_data takes 1,2, or 3 arguments (%i given)'%len(args))
    model = kwargs['model']
    
    fg = FitGui(xdata,ydata,**kwargs)
    if model is not None and not isinstance(model,FunctionModel1D):
        fg.fitmodel = True
    res = fg.edit_traits(kind='livemodal')
    
    if res:
        return fg.getModelObject()
    else:
        return None