import numpy as np
from execute import Execute

def main():
    p1 = Execute().positioned("0 0 0").rotated("0 0")
    p2 = Execute().positioned("0 10 0").rotated("0 0")
    p3 = Execute().positioned(p1).facing(p2).facing("^ ^ ^-1")
    
    # q1 = Execute()._as([p1, p2, p3]).at("@s")
    
    print(f"position: {p1.position}, rotation: {p1.rotation}")


if __name__ == "__main__":
    main()
