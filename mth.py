import numpy as np

class Mth:
    __SIN_QUANTIZATION = np.int32(65536)
    __SIN_MASK = np.int32(65535)
    __COS_OFFSET = np.int32(16384)
    __SIN_SCALE = np.float64(10430.378350470453)

    __SIN = np.fromfunction(lambda i: np.sin(i / Mth.__SIN_SCALE), __SIN_QUANTIZATION, dtype=np.float32)
    __MULTIPLY_DE_BRUIJN_BIT_POSITION = np.array([0, 1, 28, 2, 29, 14, 24, 3, 30, 22, 20, 15, 25, 17, 4, 8, 31, 27, 13, 23, 21, 19, 16, 7, 26, 12, 18, 6, 11, 5, 10, 9], dtype=np.int32)
    __ONE_SIXTH = np.float64(0.16666666666666666)
    __FRAC_EXP = np.int32(8)
    __LUT_SIZE = np.int32(257)
    __FRAC_BIAS = np.float64(np.int64(4805340802404319232).view(np.float64))
    
    @staticmethod
    def sin(i: np.float64) -> np.float32:
        index = np.int32(np.int64(i * Mth.__SIN_SCALE) & Mth.__SIN_MASK)
        return Mth.__SIN[index]
    
    @staticmethod
    def cos(i: np.float64) -> np.float32:
        index = np.int32(np.int64(i * Mth.__SIN_SCALE + np.float64(Mth.__COS_OFFSET)) & Mth.__SIN_MASK)
        return Mth.__SIN[index]
    
    @staticmethod
    def sqrt(x: np.float32) -> np.float32:
        return np.float32(np.sqrt(x))
    
    PI = np.float32(np.pi)
    HALF_PI = np.float32(np.pi / 2)
    TWO_PI = np.float32(np.pi * 2)
    DEG_TO_RAD = np.float32(np.pi / 180.0)
    RAD_TO_DEG = np.float32(180.0) / np.float32(np.pi)
    EPSILON = np.float32(1e-5)
    SQRT_OF_TWO = sqrt(np.float32(2.0))
    X_AXIS = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    Y_AXIS = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    Z_AXIS = np.array([0.0, 0.0, 1.0], dtype=np.float32)