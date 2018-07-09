import numpy as np
import cv2
from numpy.core.multiarray import ndarray
from utils.TimerProfiler import *

#feather amount to procent, serving to control the size of the area, which will be subject to the weighting q

def optimizedBlend(src, dst, mask):
    timer = TimerProfiler(False)

    timer.start()

    maskIndices = np.where(mask != 0)

    maskPts = np.hstack((maskIndices[1][:, np.newaxis], maskIndices[0][:, np.newaxis]))
    hull = cv2.convexHull(maskPts)
    timer.print_lap(timer.lap(), "hull")

    mask = np.array(mask != 0).astype(np.uint8) * 255
    cv2.fillPoly(mask, pts=[hull], color=255)
    timer.print_lap(timer.lap(), "draw poly")

    mask = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    mask = cv2.normalize(mask, mask, 0, 1.3, cv2.NORM_MINMAX)
    mask[mask > 1.0] = 1.0
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    timer.print_lap(timer.lap(), "dist transf")

    composedImg = np.copy(dst)
    transferredDst = np.copy(src)

    maskedSrc = dst[maskIndices].astype(np.int32)
    maskedDst = src[maskIndices].astype(np.int32)

    meanSrc = np.mean(maskedSrc, axis=0)
    meanDst = np.mean(maskedDst, axis=0)
    timer.print_lap(timer.lap(), "mean")

    newres = np.add(meanSrc, -meanDst)
    maskedDst = np.add(maskedDst, newres)
    maskedDst = np.clip(maskedDst, 0, 255)

    transferredDst[maskIndices] = maskedDst

    composedImg[maskIndices] = np.multiply(mask[maskIndices], transferredDst[maskIndices]) + np.multiply((1.0 - mask[maskIndices]), dst[maskIndices])
    timer.print_lap(timer.lap(), "blend")
    return composedImg