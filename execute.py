from __future__ import annotations
import numpy as np
from mth import Mth
from argument_types import *

# TODO: Context fork: as, at, facing, positioned, rotated
class Execute:
    def __init__(self):
        self.position = np.zeros(3, dtype=np.float64)
        self.rotation = np.zeros(2, dtype=np.float32)
        self.anchor = EntityAnchor.feet
        self.dimension = Dimension.overworld
    
    def align(self, axes: Swizzle) -> Execute:
        if axes & Swizzle.x:
            self.position[0] = np.floor(self.position[0])
        if axes & Swizzle.y:
            self.position[1] = np.floor(self.position[1])
        if axes & Swizzle.z:
            self.position[2] = np.floor(self.position[2])
        return self
    
    def anchored(self, anchor: EntityAnchor) -> Execute:
        self.anchor = anchor
        return self

    def _as(self, target: Execute) -> Execute:
        return self
    
    def at(self, target: Execute) -> Execute:
        self.position = target.position
        self.rotation = target.rotation
        self.dimension = target.dimension
        return self

    def facing(self, arg: np.ndarray | str | Execute, anchor: EntityAnchor=EntityAnchor.feet) -> Execute:
        pos_to = np.zeros(3, dtype=np.float64)
        if isinstance(arg, np.ndarray | str):
            pos_to = self.__to(arg)
        elif isinstance(arg, Execute):
            pos_to = arg.position if anchor == EntityAnchor.feet else arg.position + np.array([.0, 1.62, .0], dtype=np.float64)
        else:
            raise NotImplementedError("Unsupported type.")
        pos_from = self.__applyAnchor()
        xd = np.float64(pos_to[0] - pos_from[0])
        yd = np.float64(pos_to[1] - pos_from[1])
        zd = np.float64(pos_to[2] - pos_from[2])
        sd = np.sqrt(xd * xd + zd * zd, dtype=np.float64)
        
        self.rotation[0] = Mth.wrapDegrees(np.float32((Mth.atan2(zd, xd) * np.float32(180.0) / np.float32(np.pi)) - np.float32(90.0)))
        self.rotation[1] = Mth.wrapDegrees(np.float32(-(Mth.atan2(yd, sd) * np.float32(180.0) / np.float32(np.pi))))
        return self
    
    def _in(self, dimension: Dimension) -> Execute:
        self.dimension = dimension
        return self

    def positioned(self, arg: np.ndarray | str | Execute):
        if isinstance(arg, np.ndarray | str):
            pos = arg
            self.position = self.__to(pos)
            self.anchor = EntityAnchor.feet
            return self
        elif isinstance(arg, Execute):
            target = arg
            self.position = target.position
            return self
        raise NotImplementedError("Unsupported type.")

    def rotated(self, arg: np.ndarray | str | Execute):
        if isinstance(arg, np.ndarray | str):
            rot = arg
            self.rotation = self.__rot_to(rot)
            return self
        elif isinstance(arg, Execute):
            target = arg
            self.rotation = target.rotation
            return self
        raise NotImplementedError("Unsupported type.")
    
    ## Helper methods

    def __to(self, pos: np.ndarray | str) -> np.ndarray:
        if isinstance(pos, np.ndarray) and len(pos) == 3:
            return pos
        if not isinstance(pos, str):
            raise NotImplementedError("Unsupported type.")
        result_vec = np.zeros(3, dtype=np.float64)
        splited = pos.split()
        if splited[0][0] == '^':
            for i , coord in enumerate(splited):
                if splited[i][0] != '^':
                    raise ValueError('Invalid local coordinate format')
                
            local_pos = np.array(list(map(lambda x: np.float32(x[1:] if len(x) > 1 else 0), splited)), dtype=np.float64)
            result_vec = self.__applyAnchor() + applyLocalCoordinatesToRotation(self.rotation, local_pos)
        else:
            for i, coord in enumerate(splited):
                if coord[0] == '~':
                    result_vec[i] = self.position[i] + np.float64(coord[1:] if len(coord) > 1 else 0)
                else:
                    result_vec[i] = np.float64(coord)
        return result_vec
    
    def __rot_to(self, rot: np.ndarray | str) -> np.ndarray:
        if isinstance(rot, np.ndarray) and len(rot) == 2:
            return rot
        if not isinstance(rot, str):
            raise NotImplementedError("Unsupported type.")
        result_vec = np.zeros(2, dtype=np.float32)
        splited = rot.split()
        for i, r in enumerate(splited):
            if r[0] == '~':
                result_vec[i] = self.rotation[i] + np.float32(r[1:] if len(r) > 1 else 0)
            else:
                result_vec[i] = np.float32(r)
        return result_vec
    
    def __applyAnchor(self) -> np.ndarray:
        return self.position if self.anchor == EntityAnchor.feet else self.position + np.array([.0, 1.62, .0], dtype=np.float64)
        

    
def applyLocalCoordinatesToRotation(rotation: np.ndarray, direction: np.ndarray) -> np.ndarray:
    yCos = Mth.cos((rotation[0] + np.float32(90.0)) * Mth.DEG_TO_RAD)
    ySin = Mth.sin((rotation[0] + np.float32(90.0)) * Mth.DEG_TO_RAD)
    xCos = Mth.cos(-rotation[1] * Mth.DEG_TO_RAD)
    xSin = Mth.sin(-rotation[1] * Mth.DEG_TO_RAD)
    xCosUp = Mth.cos((-rotation[1] + np.float32(90.0)) * Mth.DEG_TO_RAD)
    xSinUp = Mth.sin((-rotation[1] + np.float32(90.0)) * Mth.DEG_TO_RAD)
    
    forwards = np.array([yCos * xCos, xSin, ySin * xCos], dtype=np.float64)
    up = np.array([yCos * xCosUp, xSinUp, ySin * xCosUp], dtype=np.float64)
    left = cross(forwards, up) * np.float32(-1.0)
    
    xa = np.float64(forwards[0] * direction[2] + up[0] * direction[1] + left[0] * direction[0])
    ya = np.float64(forwards[1] * direction[2] + up[1] * direction[1] + left[1] * direction[0])
    za = np.float64(forwards[2] * direction[2] + up[2] * direction[1] + left[2] * direction[0])
    
    return np.array([xa, ya, za], dtype=np.float64)

def cross(v1:np.ndarray, v2:np.ndarray) -> np.ndarray:
        return np.array([v1[1] * v2[2] - v1[2] * v2[1], 
                         v1[2] * v2[0] - v1[0] * v2[2],
                         v1[0] * v2[1] - v1[1] * v2[0]], dtype=np.float64)