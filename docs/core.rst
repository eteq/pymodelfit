Core Module - Base Classes and Main Functions 
=============================================

.. automodule:: pymodelfit.core


Class Inheritance Diagram
-------------------------

:mod:`pymodelfit.core` includes a number of classes that are primarily inteded to be
subclassed by particular models.  The relationship between these classes is shown
in the below diagram.

.. inheritance-diagram:: pymodelfit.core
   :parts: 1
   

Module Reference
----------------


Classes
^^^^^^^
.. autosummary::
    :toctree: core
    
    ModelTypeError
    ParametricModel
    AutoParamsMeta
    InputCoordinateTransformer
    FunctionModel
    CompositeModel
    FunctionModel1D
    FunctionModel1DAuto
    DatacentricModel1D
    DatacentricModel1DAuto
    CompositeModel1D
    FunctionModel2DScalar
    FunctionModel2DScalarAuto
    FunctionModel2DScalarDeformedRadial
    FunctionModel2DScalarSeperable
    CompositeModel2DScalar
    ModelSequence
    

Functions
^^^^^^^^^
.. autosummary::
    :toctree: core
    
    register_model
    list_models
    get_model_class
    get_model_instance
    offset_model
    scale_model
    scale_and_offset_model
    intersect_models
