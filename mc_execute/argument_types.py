from enum import Enum, IntFlag

class Dimension(Enum):
    overworld = 0
    nether = 1
    end = 2
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            if value in cls.__members__:
                return cls[value]
        raise ValueError(f"Invalid Dimension type.\nExpected: {list(cls.__members__.keys())}")

class EntityAnchor(Enum):
    eyes = 0
    feet = 1
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            if value in cls.__members__:
                return cls[value]
        raise ValueError(f"Invalid EntityAnchor type.\nExpected: {list(cls.__members__.keys())}")

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

class Swizzle(IntFlag):
    none = 0
    x = 1
    y = 1 << 1
    z = 1 << 2
    xy = yx = x | y
    yz = zy = y | z
    zx = xz = z | x
    xyz = xzy = yxz = yzx = zxy = zyx = x | y | z
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            if value in cls.__members__:
                return cls[value]
        raise ValueError(f"Invalid Swizzle type.\nExpected: {list(cls.__members__.keys())}")
