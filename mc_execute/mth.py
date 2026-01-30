import numpy as np

SIN_QUANTIZATION = np.int32(65536)
SIN_MASK = np.int32(65535)
COS_OFFSET = np.int32(16384)
SIN_SCALE = np.float64(10430.378350470453)
MULTIPLY_DE_BRUIJN_BIT_POSITION = np.array([0, 1, 28, 2, 29, 14, 24, 3, 30, 22, 20, 15, 25, 17, 4, 8, 31, 27, 13, 23, 21, 19, 16, 7, 26, 12, 18, 6, 11, 5, 10, 9], dtype=np.int32)
ONE_SIXTH = np.float64(0.16666666666666666)
FRAC_EXP = np.int32(8)
LUT_SIZE = np.int32(257)
FRAC_BIAS = np.float64(np.int64(4805340802404319232).view(np.float64))
class Mth:
    __SIN = np.fromfunction(lambda i: np.float32(np.sin(i / SIN_SCALE)), (SIN_QUANTIZATION,), dtype=np.float32)
    __ASIN_TAB = np.fromfunction(lambda i: np.arcsin(np.double(i / 256.0)), (257,), dtype=np.float64)
    __COS_TAB = np.cos(__ASIN_TAB, dtype=np.float64)
    
    @staticmethod
    def sin(i: np.float64) -> np.float32:
        index = np.int32(np.int64(i * SIN_SCALE) & SIN_MASK)
        return Mth.__SIN[index]
    
    @staticmethod
    def cos(i: np.float64) -> np.float32:
        index = np.int32(np.int64(i * SIN_SCALE + np.float64(COS_OFFSET)) & SIN_MASK)
        return Mth.__SIN[index]
    
    @staticmethod
    def sqrt(x: np.float32) -> np.float32:
        return np.float32(np.sqrt(x))
    
    @staticmethod
    def wrapDegrees(angle: np.float32) -> np.float32:
        normalizedAngle = np.fmod(angle, np.float32(360.0), dtype=np.float32)
        if normalizedAngle >= np.float32(180.0):
            normalizedAngle -= np.float32(360.0)
        if normalizedAngle < np.float32(-180.0):
            normalizedAngle += np.float32(360.0)
        
        return normalizedAngle
    
    @staticmethod
    def atan2(y: np.float64, x:np.float64) -> np.float64:
        d2 = x * x + y * y
        if np.isnan(d2):
            return np.float64(np.nan)
        negY = y < np.float64(0.0)
        if negY: y = np.float64(-1.0) * y
        negX = x < np.float64(0.0)
        if negX: x = np.float64(-1.0) * x
        steep = y > x
        if steep:
            x, y = (y, x)
            
        rinv = Mth.fastInvSqrt(d2)
        x *= rinv
        y *= rinv
        yp = FRAC_BIAS + y
        index = np.int32(yp.view(np.int64))
        phi = Mth.__ASIN_TAB[index]
        cPhi = Mth.__COS_TAB[index]
        sPhi = yp - FRAC_BIAS
        sd = y * cPhi - x * sPhi
        d =(np.float64(6.0) + sd * sd) * sd * ONE_SIXTH
        theta = phi + d
        
        if steep: theta = np.float64(np.pi) / np.float64(2.0) - theta
        if negX: theta = np.float64(np.pi) - theta
        if negY: theta = np.float64(-1.0) * theta
        
        return theta
        
    @staticmethod
    def fastInvSqrt(x: np.float64) -> np.float64:
        xhalf = np.float64(0.5) * x
        i = np.int64(x.view(np.int64))
        i = np.int64(6910469410427058090) - (i >> 1)
        x = i.view(np.float64)
        
        return x * (np.float64(1.5) - xhalf * x * x)
    
    # static members
    PI = np.float32(np.pi)
    HALF_PI = np.float32(np.pi / 2)
    TWO_PI = np.float32(np.pi * 2)
    DEG_TO_RAD = np.float32(np.pi) / np.float32(180.0)
    RAD_TO_DEG = np.float32(180.0) / np.float32(np.pi)
    EPSILON = np.float32(1e-5)
    SQRT_OF_TWO = sqrt(np.float32(2.0))
    X_AXIS = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    Y_AXIS = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    Z_AXIS = np.array([0.0, 0.0, 1.0], dtype=np.float32)