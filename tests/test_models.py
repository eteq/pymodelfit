#!/usr/bin/env python
from __future__ import division,with_statement
import numpy as np
from nose import tools
from pymodelfit import core,builtins

def test_1d_model_funcs():    
    for modname in core.list_models(baseclass=core.FunctionModel1D):
        cls = core.get_model_class(modname)
        # ignore datacentric models because they are data-dependant
        if not issubclass(cls,core.DatacentricModel1D):
            #test both ways of generating the model instance
            if core.get_model_class(modname).isVarnumModel():
                #just try it w/ 3 variable arguments w/ default values
                mod = cls(3,)
                mod = core.get_model_instance(modname,nvarparams=3)
            else:
                mod = cls()
                mod = core.get_model_instance(modname)
                
            if mod.rangehint is None:
                x1 = 0
                x2 = 01
            else:
                x1,x2 = mod.rangehint
               
            avgval = mod((x1+x2)/2) #single value output
            rangevals = mod(np.linspace(x1,x2,12)[1:-1]) #array output
            
            assert np.all(np.isfinite(avgval)),'Non-finite value encountered for model '+modname
            assert np.all(np.isfinite(rangevals)),'Non-finite value encountered for model '+modname
            
def test_scale_off():
    m1 = core.scale_and_offset_model(builtins.LinearModel(2.5,1),scaleval=3,offsetval=-2.1)
    shouldval = 8.4
    tools.assert_almost_equal(m1(1),shouldval,msg='Scale and Offset of model not giving correct answer: %g,%g'%(m1(1),shouldval))
    
    m2 = core.offset_model(builtins.PowerLawModel(1.2,3),offsetval=2)
    shouldval = 1.2*2**3+2
    tools.assert_almost_equal(m2(2),shouldval,msg='Offset of model not giving correct answer: %g,%g'%(m2(2),shouldval))
    
    m3 = core.scale_model(builtins.PolynomialModel(3,c0=0,c1=2.1,c2=-3.5),scaleval=1.3)
    shouldval = 1.3*(2.1*3-3.5*3**2)
    tools.assert_almost_equal(m3(3),shouldval,msg='Scale of model not giving correct answer: %g,%g'%(m3(3),shouldval))
    
if __name__ == '__main__':
    import nose
    nose.main()
