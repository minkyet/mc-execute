from __future__ import annotations
import numpy as np
from .mth import Mth
from .argument_types import Dimension, EntityAnchor, Swizzle

class Execute:
    def __init__(self, target: Execute | Entity | None = None):
        if isinstance(target, Execute):
            self.__entities = list(target.entities)
            self.__positions = target.positions.copy()
            self.__rotations = target.rotations.copy()
            self.__dimensions = list(target.dimensions)
            self.anchor = target.anchor
        else:
            if isinstance(target, Entity):
                self.__entities = [target]
                self.__positions = np.array([target.position], dtype=np.float64)
                self.__rotations = np.array([target.rotation], dtype=np.float32)
                self.__dimensions = [target.dimension]
            else:
                self.__entities = [None]    # "None" for non-entity(SERVER) context
                self.__positions = np.zeros((1, 3), dtype=np.float64)
                self.__rotations = np.zeros((1, 2), dtype=np.float32)
                self.__dimensions = [Dimension.overworld]
            self.anchor: EntityAnchor = EntityAnchor.feet
    
    ## properites

    @property
    def entities(self) -> list[Entity]:
        return self.__entities

    @property
    def positions(self) -> np.ndarray[np.dtype[np.float64]]:
        return self.__positions
    
    @property
    def rotations(self) -> np.ndarray[np.dtype[np.float32]]:
        return self.__rotations
    
    @property
    def dimensions(self) -> list[Dimension]:
        return self.__dimensions
    
    ## execute methods
    
    def align(self, axes: Swizzle | str) -> Execute:
        if isinstance(axes, str): axes = Swizzle(axes)
        
        if axes & Swizzle.x:
            self.__positions[:, 0] = np.floor(self.__positions[:, 0])
        if axes & Swizzle.y:
            self.__positions[:, 1] = np.floor(self.__positions[:, 1])
        if axes & Swizzle.z:
            self.__positions[:, 2] = np.floor(self.__positions[:, 2])
        return self

    def anchored(self, anchor: EntityAnchor | str) -> Execute:
        if isinstance(anchor, str): anchor = EntityAnchor(anchor)
        self.anchor = anchor
        return self

    def as_(self, target: Entity | list[Entity]) -> Execute:
        fork_target = [target] if isinstance(target, Entity) else target
        self.__fork(entities=fork_target)
        return self

    def at(self, target: Entity | list[Entity] | str = "@s") -> Execute:
        if target == "@s":
            if any(e is None for e in self.__entities):
                raise ValueError("Cannot execute 'at @s' from a non-entity source.")
            self.__positions = np.array([i.position for i in self.__entities], dtype=np.float64)
            self.__rotations = np.array([i.rotation for i in self.__entities], dtype=np.float32)
        else:
            at_target = [target] if isinstance(target, Entity) else target
            at_positions = np.array([i.position for i in at_target], dtype=np.float64)
            at_rotations = np.array([i.rotation for i in at_target], dtype=np.float32)
            at_dimensions = [i.dimension for i in at_target]
            self.__fork(positions=at_positions, rotations=at_rotations, dimensions=at_dimensions)
        return self

    def facing(self, arg: Entity | list[Entity] | np.ndarray | str = "@s", anchor: EntityAnchor | str = EntityAnchor.feet) -> Execute:
        if isinstance(anchor, str): anchor = EntityAnchor(anchor)
        if isinstance(arg, str) and arg == "@s":
            if any(e is None for e in self.__entities):
                raise ValueError("Cannot execute 'facing entity @s' from a non-entity source.")
            rotations = []
            for facing_from, facing_to in zip(self.__applyAnchor(), self.__entities):
                delta = facing_to.getAnchoredPosition(anchor) - facing_from
                rotations.append(self.__getFacingRotation(delta))
            self.__rotations = np.array(rotations)
        elif isinstance(arg, np.ndarray):
            facing_from = self.__applyAnchor() # (N, 3)
            if arg.ndim == 1 and arg.shape[0] == 3:
                deltas = arg - facing_from
                self.__rotations = np.array([self.__getFacingRotation(delta) for delta in deltas])
            elif arg.ndim == 2 and arg.shape[1] == 3:
                num_sources = len(facing_from)
                num_targets = len(arg)
                sources_expanded = np.repeat(facing_from, num_targets, axis=0)
                targets_expanded = np.tile(arg, (num_sources, 1))
                deltas = targets_expanded - sources_expanded
                rots = np.array([self.__getFacingRotation(delta) for delta in deltas])
                self.__fork(rotations=rots, isAlreadyForked=True)
            else:
                raise ValueError(f"Invalid facing coordinate shape: {arg.shape}. Expected (3,) or (N, 3).")
        elif isinstance(arg, str):
            facing_from = self.__applyAnchor()
            facing_to = self.__to(arg)
            deltas = facing_to - facing_from
            self.__rotations = np.array([self.__getFacingRotation(delta) for delta in deltas])
        else:
            facing_target = [arg] if isinstance(arg, Entity) else arg
            facing_from = self.__applyAnchor()
            facing_to = np.array([i.getAnchoredPosition(anchor) for i in facing_target])
            deltas = np.tile(facing_to, (len(facing_from), 1)) - np.repeat(facing_from, len(facing_to), axis=0)
            rots = np.array([self.__getFacingRotation(delta) for delta in deltas])
            self.__fork(rotations=rots, isAlreadyForked=True)

        return self
    
    def in_(self, dimension: Dimension) -> Execute:
        self.__dimensions = [dimension] * len(self.__dimensions)
        return self

    def positioned(self, arg: np.ndarray | Entity | list[Entity] | str = "@s") -> Execute:
        if isinstance(arg, str) and arg == "@s":
            if any(e is None for e in self.__entities):
                raise ValueError("Cannot execute 'positioned as @s' from a non-entity source.")
            self.__positions = np.array([i.position for i in self.__entities], dtype=np.float64)
        elif isinstance(arg, np.ndarray):
            if arg.ndim == 2 and arg.shape[1] == 3:
                self.__fork(positions=arg)
            elif arg.ndim == 1 and len(arg) == 3:
                self.__positions = self.__to(arg)
            else:
                raise ValueError(f"Invalid position array shape: {arg.shape}. Expected (3,) or (N, 3).")
            self.anchor = EntityAnchor.feet
        elif isinstance(arg, str):
            self.__positions = self.__to(arg)
            self.anchor = EntityAnchor.feet
        else:
            target = arg
            pos_target = [target] if isinstance(target, Entity) else target
            pos = np.array([i.position for i in pos_target], dtype=np.float64)
            self.__fork(positions=pos)

        return self

    def rotated(self, arg: np.ndarray | Entity | list[Entity] | str = "@s") -> Execute:
        if isinstance(arg, str) and arg == "@s":
            if any(e is None for e in self.__entities):
                raise ValueError("Cannot execute 'rotated as @s' from a non-entity source.")
            self.__rotations = np.array([i.rotation for i in self.__entities], dtype=np.float32)
        elif isinstance(arg, np.ndarray):
            if arg.ndim == 2 and arg.shape[1] == 2:
                self.__fork(rotations=arg)
            elif arg.ndim == 1 and len(arg) == 2:
                self.__rotations = self.__rot_to(arg)
            else:
                raise ValueError(f"Invalid rotation array shape: {arg.shape}. Expected (2,) or (N, 2).")
        elif isinstance(arg, str):
            self.__rotations = self.__rot_to(arg)
        else:
            target = arg
            rot_target = [target] if isinstance(target, Entity) else target
            rot = np.array([i.rotation for i in rot_target], dtype=np.float32)
            self.__fork(rotations=rot)

        return self
    
    ## Helper methods

    def __to(self, to: np.ndarray | str) -> np.ndarray:
        positions = self.__applyAnchor() if isinstance(to, str) and '^' in to else self.__positions
        return np.array([parseCoordinates(pos, rot, to) for pos, rot in zip(positions, self.__rotations)])

    def __rot_to(self, to: np.ndarray | str) -> np.ndarray:
        return np.array([parseRotation(rot, to) for rot in self.__rotations])
    
    def __getFacingRotation(self, delta: np.ndarray) -> np.ndarray:
        xd = delta[0]
        yd = delta[1]
        zd = delta[2]
        sd = np.sqrt(xd * xd + zd * zd, dtype=np.float64)
        return np.array([
            Mth.wrapDegrees(np.float32((Mth.atan2(zd, xd) * np.float32(180.0) / np.float32(np.pi)) - np.float32(90.0))),
            Mth.wrapDegrees(np.float32(-(Mth.atan2(yd, sd) * np.float32(180.0) / np.float32(np.pi))))
        ])
    
    def __applyAnchor(self) -> np.ndarray:
        if self.anchor == EntityAnchor.eyes:
            return np.array([pos + np.array([.0, entity.eye_level, .0], dtype=np.float64) for pos, entity in zip(self.__positions, self.__entities)])
        else: 
            return self.__positions

    def __fork(self, entities:list[Entity] = None, dimensions:list[Dimension] = None, positions: np.ndarray = None, rotations: np.ndarray = None, isAlreadyForked = False):
        targets = [x for x in [entities, dimensions, positions, rotations] if x is not None]
        if not targets:
            raise ValueError('Invalid fork target format: No target provided.')
        
        prev_count = len(self.__entities)
        fork_count = int(len(targets[0]) / prev_count) if isAlreadyForked else len(targets[0])
        
        if fork_count == 0 or prev_count == 0:
            self.__entities = []
            self.__positions = np.empty((0, 3))
            self.__rotations = np.empty((0, 2))
            self.__dimensions = []
            return
        
        # Repeat unchanged contexts: (A, B) -> (A, A, A, B, B, B)
        self.__entities = [i for i in self.__entities for _ in range(fork_count)]
        self.__positions = np.repeat(self.__positions, fork_count, axis=0)
        self.__rotations = np.repeat(self.__rotations, fork_count, axis=0)
        self.__dimensions = [i for i in self.__dimensions for _ in range(fork_count)]
        
        # Tile changed contexts: (P, Q, R) -> (P, Q, R, P, Q, R)
        # result(Cartesian product): ((A, P), (A, Q), (A, R), (B, P), (B, Q), (B, R))
        if entities is not None:
            self.__entities = entities if isAlreadyForked else entities * prev_count
        if dimensions is not None:
            self.__dimensions = dimensions if isAlreadyForked else dimensions * prev_count
        if positions is not None:
            self.__positions = positions if isAlreadyForked else np.tile(positions, (prev_count, 1))
        if rotations is not None:
            self.__rotations = rotations if isAlreadyForked else np.tile(rotations, (prev_count, 1))

class Entity:
    def __init__(self, target: Execute | Entity | None = None):
        self.position: np.ndarray[np.dtype[np.float64]] = np.zeros(3, dtype=np.float64)
        self.rotation: np.ndarray[np.dtype[np.float32]] = np.zeros(2, dtype=np.float32)
        self.dimension: Dimension = Dimension.overworld
        self.eye_level: np.float64 = np.float64(0.)
        
        if isinstance(target, Execute):
            self.position = target.positions[-1].copy()
            self.rotation = target.rotations[-1].copy()
            self.dimension = Dimension(target.dimensions[-1])
        elif isinstance(target, Entity):
            self.position = target.position.copy()
            self.rotation = target.rotation.copy()
            self.dimension = Dimension(target.dimension)
            self.eye_level = target.eye_level.copy()
        
    def setEyeLevel(self, height: float | np.float64 = np.float64(0.)) -> Entity:
        self.eye_level = np.float64(height)
        return self
    
    def getAnchoredPosition(self, anchor: str | EntityAnchor = EntityAnchor.feet) -> np.ndarray[np.dtype[np.float64]]:
        anchor = EntityAnchor(anchor) if isinstance(anchor, str) else anchor
        return self.position if anchor == EntityAnchor.feet else self.position + np.array([.0, self.eye_level, .0], dtype=np.float64)

    def tp(self, pos: np.ndarray | str, dimension: Dimension = None) -> Entity:
        if isinstance(pos, str) and len(pos.split()) == 5:
            splitted = pos.split()
            self.position = parseCoordinates(self.position, self.rotation, ' '.join(splitted[:3]))
            self.rotate(' '.join(splitted[3:]))
        else:
            self.position = parseCoordinates(self.position, self.rotation, pos)
            
        if dimension:
            dimension = Dimension(dimension) if isinstance(dimension, str) else dimension
            self.dimension = dimension
        return self
        
    def rotate(self, rot: np.ndarray | str) -> Entity:
        self.rotation = parseRotation(self.rotation, rot, isEntity=True)
        return self
    
    def setDimension(self, dimension: str | Dimension = Dimension.overworld) -> Entity:
        dimension = Dimension(dimension) if isinstance(dimension, str) else dimension
        self.dimension = dimension
        return self
        
def parseRotation(rotation: np.ndarray, to: np.ndarray | str, isEntity:bool = False) -> np.ndarray:        
    if isinstance(to, np.ndarray) and len(to) == 2:
        return np.array([Mth.wrapDegrees(i) for i in to])
    if not isinstance(to, str):
        raise NotImplementedError("Unsupported type.")
    
    result_vec = np.zeros(2, dtype=np.float32)
    splited = to.split()
    result_vec[0] = Mth.wrapDegrees(rotation[0] + np.float32(splited[0][1:] if len(splited[0]) > 1 else 0) if splited[0][0] == '~' else np.float32(splited[0]))
    if isEntity:
        result_vec[1] = np.float32(np.clip(rotation[1] + np.float32(splited[1][1:] if len(splited[1]) > 1 else 0) if splited[1][0] == '~' else np.float32(splited[1]), -90.0, 90.0))
    else:
        result_vec[1] = np.float32(rotation[1] + np.float32(splited[1][1:] if len(splited[1]) > 1 else 0) if splited[1][0] == '~' else np.float32(splited[1]))
    return result_vec

def parseCoordinates(position: np.ndarray, rotation: np.ndarray, to: np.ndarray | str) -> np.ndarray:
    if isinstance(to, np.ndarray) and len(to) == 3:
        return to
    if not isinstance(to, str):
        raise NotImplementedError("Unsupported type.")

    result_vec = np.zeros(3, dtype=np.float64)
    splited = to.split()
    
    if splited[0][0] == '^':
        for i , _ in enumerate(splited):
            if splited[i][0] != '^':
                raise ValueError('Invalid local coordinate format.')
        local_pos = np.array(list(map(lambda x: np.float32(x[1:] if len(x) > 1 else 0), splited)), dtype=np.float64)
        result_vec = position + applyLocalCoordinatesToRotation(rotation, local_pos)
    else:
        for i, part in enumerate(splited):
            if part[0] == '~':
                result_vec[i] = position[i] + np.float64(part[1:] if len(part) > 1 else 0)
            else:
                val = float(part)
                if i == 1:
                    result_vec[i] = np.float64(val)
                    continue
                if '.' in part:
                    result_vec[i] = np.float64(val)
                else:
                    result_vec[i] = np.float64(val + 0.5)
    return result_vec

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