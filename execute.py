from __future__ import annotations
import warnings
from functools import singledispatchmethod
import numpy as np
from mth import Mth
from argument_types import *

class Execute:
    def __init__(self):
        self.position = np.zeros(3, dtype=np.float64)
        self.rotation = np.zeros(2, dtype=np.float32)
        self.dimension = Dimension.overworld
    
    def align(self, axes: Swizzle) -> Execute:
        return self
    
    def anchored(self, anchor: EntityAnchor) -> Execute:
        return self
    
    def _as(self, targets: Execute) -> Execute:
        return self
    
    def at(self, targets: Execute) -> Execute:
        return self
    
    def facing(self, arg: np.ndarray | Execute, anchor: EntityAnchor=EntityAnchor.feet) -> Execute:
        if isinstance(arg, np.ndarray):
            pos = arg
            return self
        elif isinstance(arg, Execute):
            target = arg
            return self
        
        raise NotImplementedError("Unsupported type.")
    
    def _in(self, dimension: Dimension) -> Execute:
        self.dimension = dimension
        return self
    
    @singledispatchmethod
    def positioned(self, _):
        raise NotImplementedError("Unsupported type.")
    
    @positioned.register
    def _(self, pos: np.ndarray) -> Execute:
        return self
    
    @positioned.register
    def _(self, targets: Execute) -> Execute:
        return self
    
    @singledispatchmethod
    def rotated(self, _):
        raise NotImplementedError("Unsupported type.")
    
    @rotated.register
    def _(self, rot: np.ndarray) -> Execute:
        return self
    
    @rotated.register
    def _(self, targets: Execute) -> Execute:
        return self