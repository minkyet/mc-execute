from enum import Enum
import numpy as np

class Dimension(Enum):
    overworld = 0
    nether = 1
    end = 2

class EntityAnchor(Enum):
    eyes = 0
    feet = 1

class EntityRelation(Enum):
    attacker = 0
    controller = 1
    leasher = 2
    origin = 3
    owner = 4
    passengers = 5
    target = 6
    vehicle = 7

class HeightMap(Enum):
    world_surface = 0
    motion_blocking = 1
    motion_blocking_no_leaves = 2
    ocean_floor = 3

class Swizzle(Enum):
    x = 1
    y = 1 << 1
    z = 1 << 2
    xy = yx = x | y
    yz = zy = y | z
    zx = xz = z | x
    xyz = xzy = yxz = yzx = zxy = zyx = x | y | z
    
# class Vector3:
#     def __init__(self, *args):
#         if isinstance(args[0], np.ndarray) and len(args[0]) == 3:
#             self.value = np.float64(args[0])
#         elif isinstance(args[0], str):
#             string = args[0]
#         elif len(args) == 3:
#             x, y, z = args
#             self.value = np.array([x, y, z], dtype=np.float64)
#         else:
#             raise NotImplementedError("Invalid constructor type.")