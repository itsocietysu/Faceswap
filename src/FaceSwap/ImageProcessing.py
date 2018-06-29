import numpy as np
import cv2
from utils.TimerProfiler import *
#tutaj src to obraz, z ktorego piksele beda wklejane do obrazu dst
#feather amount to procent, sluzacy do sterowania wielkoscia obszaru, ktory bedzie poddany wagowaniu q
def blendImages(src, dst, mask):
    timer = TimerProfiler(False)

    timer.start()

    maskFirst = mask.copy()
    maskIndices = np.where(mask != 0)
    maskPts = np.hstack((maskIndices[1][:, np.newaxis], maskIndices[0][:, np.newaxis]))
    hull = cv2.convexHull(maskPts)
    timer.print_lap(timer.lap(), "hull")

    mask = np.array(mask != 0).astype(np.uint8) * 255
    cv2.fillPoly(mask, pts=[hull], color=255)
    maskIndices = (mask != 0)
    timer.print_lap(timer.lap(), "draw poly")
    mask = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    mask = cv2.normalize(mask, mask, 0, 1.3, cv2.NORM_MINMAX)
    mask[mask > 1.0] = 1.0
    mask[maskFirst == 0] = 0
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    timer.print_lap(timer.lap(), "dist transf")

    composedImg = np.copy(dst)
    composedImg[maskIndices] = (mask[maskIndices]) * src[maskIndices] + (1.0 - mask[maskIndices]) * dst[maskIndices]
    timer.print_lap(timer.lap(), "blend")
    return composedImg

#uwaga, tutaj src to obraz, z ktorego brany bedzie kolor
def colorTransfer(src, dst, mask):
    transferredDst = np.copy(dst)
    #indeksy nie czarnych pikseli maski
    maskIndices = np.where(mask != 0)
    #src[maskIndices[0], maskIndices[1]] zwraca piksele w nie czarnym obszarze maski

    maskedSrc = src[maskIndices].astype(np.int32)
    maskedDst = dst[maskIndices].astype(np.int32)

    meanSrc = np.mean(maskedSrc, axis=0)
    meanDst = np.mean(maskedDst, axis=0)

    newres = np.add(meanSrc, -meanDst)
    maskedDst = np.add(maskedDst, newres)
    maskedDst = np.clip(maskedDst, 0, 255)

    transferredDst[maskIndices] = maskedDst

    return transferredDst

