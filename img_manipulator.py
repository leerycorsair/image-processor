
from skimage import util, restoration, filters, img_as_ubyte
from scipy.signal import convolve2d
import numpy as np

import cv2
from cv2 import dnn_superres

from skimage.filters.rank import mean, median, mean_bilateral
from skimage.morphology import disk, square


class ImgManipulator():

    @staticmethod
    def blur_image(img):
        sigma = 3.0
        blurred = filters.gaussian(
            img, sigma=(sigma, sigma), truncate=3.5, multichannel=True)
        return blurred

    @staticmethod
    def add_noise(img, mode):
        noise_img = util.random_noise(img, mode=mode)
        return noise_img

    @staticmethod
    def noise_canceling(img, method, footprint, fp_size):
        methods = {"Mean": mean,
                   "Median": median,
                   "Bilateral": mean_bilateral}
        footprints = {"Square": square,
                      "Disk": disk}
        denoised_img = methods[method](img, footprints[footprint](fp_size))
        return denoised_img

    @staticmethod
    def deconv(img, mode):
        psf = np.ones((5, 5)) / 25
        img = convolve2d(img, psf, 'same')
        if mode == "Richardson-Lucy Method":
            return restoration.richardson_lucy(img, psf)
        elif mode == "Wiener Method":
            return restoration.unsupervised_wiener(img, psf)[0]

    @staticmethod
    def upscale(img, modelname, modeltype, scalesize):
        sr = dnn_superres.DnnSuperResImpl_create()
        img = img_as_ubyte(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        path = "./models/"+modelname+".pb"
        sr.readModel(path)
        sr.setModel(modeltype, scalesize)
        upscaled = sr.upsample(img)
        upscaled = cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB)
        return upscaled
