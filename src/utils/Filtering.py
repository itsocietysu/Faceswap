import numpy as np
import cv2


class Filtering:
    def __init__(self):
        self.methods = {
            'contrast': self.Contrast,
            'brighness': self.Brighness,
            'warm': self.Warm,
            'saturation': self.Saturation,
            'sharpen': self.Sharpen
        }
        return

    def filter(self, img, list_params):
        for _ in list_params:
            if _ != 'name' and int(list_params[_]) != 0:
                img = self.methods[_](img, list_params[_])

        return img

    def blendTwoImages(self, src1, src2, dst):
        img1 = cv2.imread(src1)
        img2 = cv2.imread(src2, -1)

        if (img2):
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation = cv2.INTER_CUBIC)

            alpha = img1.copy().astype(np.float32)
            alpha[:, :, 0] = img2[:, :, 3] / 255.0
            alpha[:, :, 1] = img2[:, :, 3] / 255.0
            alpha[:, :, 2] = img2[:, :, 3] / 255.0

            res = img1[:, :] * (1 - alpha[:, :]) + img2[:, :, 0:3] * (alpha[:, :])
            cv2.imwrite(dst, res)

    #adjust -100:100
    def Contrast(self, src, adjust):
        adjust = int(adjust)
        adjust = (adjust + 100.0) / 100.0
        adjust = adjust * adjust

        dst = src.copy().astype(np.float32)

        dst = np.maximum(np.minimum((((dst / 255.0 - 0.5) * adjust + 0.5) * 255.0), 255), 0)

        return dst.astype(np.uint8)

    #adjust -100:100
    def Brighness(self, src, adjust):
        adjust = int(adjust)
        adjust = (255.0 * adjust / 100.0)

        dst = src.copy().astype(np.float32)

        #dst[:,:,2] = np.maximum(np.minimum((dst[:,:,2] + adjust), 255), 0)
        #dst[:,:,1] = np.maximum(np.minimum((dst[:,:,1] + adjust), 255), 0)
        #dst[:,:,0] = np.maximum(np.minimum((dst[:,:,0] + adjust), 255), 0)
        dst = np.maximum(np.minimum((dst + adjust), 255), 0)

        return dst.astype(np.uint8)

    #val 0:100
    def Warm(self, src, val):
        val = int(val)
        adjust = val / 100.0

        dst = src.copy().astype(np.float32)

        dst[:,:,2] = np.maximum(np.minimum((src[:,:,2] * (1 - (0.607 * adjust))) + (src[:,:,1] * (0.769 * adjust)) +       (src[:,:,0] * (0.189 * adjust)), 255), 0)
        dst[:,:,1] = np.maximum(np.minimum((src[:,:,2] * (0.349 * adjust)) +       (src[:,:,1] * (1 - (0.314 * adjust))) + (src[:,:,0] * (0.168 * adjust)), 255), 0)
        dst[:,:,0] = np.maximum(np.minimum((src[:,:,2] * (0.272 * adjust)) +       (src[:,:,1] * (0.534 * adjust)) +       (src[:,:,0] * (1- (0.869 * adjust))), 255), 0)

        return dst.astype(np.uint8)

    #adjust -100:100
    def Saturation(self, src, adjust):
        adjust = int(adjust)
        adjust *= -0.01
        localsrc = src.astype(np.float32)

        b, g, r = cv2.split(localsrc)

        maxvals = np.maximum(b, g, r)

        dst = localsrc.copy()

        dst[:,:,0][maxvals != b] += ((maxvals - b) * adjust)[maxvals != b]
        dst[:,:,1][maxvals != g] += ((maxvals - g) * adjust)[maxvals != g]
        dst[:,:,2][maxvals != r] += ((maxvals - r) * adjust)[maxvals != r]

        dst[:, :, 0] = np.maximum(np.minimum(dst[:, :, 0], 255), 0)
        dst[:, :, 1] = np.maximum(np.minimum(dst[:, :, 1], 255), 0)
        dst[:, :, 2] = np.maximum(np.minimum(dst[:, :, 2], 255), 0)

        return dst

    #val 0:100
    def Sharpen(self, src, val):
        val = int(val)
        amt = val / 100.0
        dst = cv2.filter2D(src, cv2.CV_32F, np.array([0, -amt, 0, -amt, 4 * amt + 1, -amt, 0, -amt, 0]))
        dst = np.maximum(np.minimum(dst, 255), 0)

        return dst.astype(np.uint8)
