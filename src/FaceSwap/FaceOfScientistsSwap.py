import dlib
import cv2
import numpy as np
import scipy

import models
import NonLinearLeastSquares
import ImageProcessing

from drawing import *

import FaceRendering
import RenderDevice
import utils_fs

from utils.TimerProfiler import *

DETS_UPDATE = 1

class FaceOfScientistsSwap:
    def __init__(self, cam_shape, images):
        self._predictor_path = "./data/assets/shape_predictor_68_face_landmarks.dat"
        self._max_image_size_for_detection = 320

        self._detector = dlib.get_frontal_face_detector()
        self._predictor = dlib.shape_predictor(self._predictor_path)

        self._mean3DShape, self._blendshapes, self._mesh, \
        self._idxs3D, self._idxs2D = utils_fs.load3DFaceModel("./data/assets/candide.npz")

        self._projection_model = models.OrthographicProjectionBlendshapes(self._blendshapes.shape[0])

        self._renderer_device = RenderDevice.RenderDevice(cam_shape[1], cam_shape[0], self._mesh)

        self._rederers_for_images = self._get_renderers_for_images(cam_shape, images)

        self._last_id_scientist = 0

        self._current_render_scientist = self._rederers_for_images[self._last_id_scientist]
        self.dets = None
        self.last_dets_update = 0

    def _get_renderers_for_images(self, cam_shape, images):
        data = []

        for img in images:
            texture_coords = utils_fs.getFaceTextureCoords(img, self._mean3DShape, self._blendshapes, self._idxs2D,
                                                           self._idxs3D, self._detector, self._predictor)

            renderer = FaceRendering.FaceRenderer(cam_shape, img, texture_coords, self._renderer_device)
            data.append(renderer)

        return data

    def get_replacement_image(self, camera_img, id_scientist):
        timer = TimerProfiler(True)

        timer.start()
        if camera_img is None:
            raise AttributeError("Image isn't valid")

        if id_scientist >= len(self._rederers_for_images):
            raise AttributeError("ID '" + id_scientist + "' doesn't exist")

        if self.last_dets_update >= DETS_UPDATE:
            self.last_dets_update = 0
            self.dets = None

        shapes2D, self.dets = utils_fs.getFaceKeypoints(camera_img, self._detector, self._predictor,
                                                    self.dets, self._max_image_size_for_detection)
        self.last_dets_update += 1

        timer.log_lap(timer.lap(), "Detect")

        if self._last_id_scientist != id_scientist:
            self._last_id_scientist = id_scientist
            self._current_render_scientist = self._rederers_for_images[id_scientist]

        if shapes2D is not None:
            for shape2D in shapes2D:
                # 3D model parameter initialization
                model_params = self._projection_model.getInitialParameters(self._mean3DShape[:, self._idxs3D],
                                                                          shape2D[:, self._idxs2D])

                timer.log_lap(timer.lap(), "projection")

                # 3D model parameter optimization
                model_params = NonLinearLeastSquares.GaussNewton(model_params, self._projection_model.residual,
                                                                 self._projection_model.jacobian,
                                                                 ([self._mean3DShape[:, self._idxs3D],
                                                                   self._blendshapes[:, :, self._idxs3D]],
                                                                  shape2D[:, self._idxs2D]),
                                                                 verbose=0)

                timer.log_lap(timer.lap(), "Gauss Newton")

                # rendering the model to an image
                shape3D = utils_fs.getShape3D(self._mean3DShape, self._blendshapes, model_params)
                timer.log_lap(timer.lap(), "Get shape")
                faceTex = self._current_render_scientist.get_face_texture()
                faceCords = self._current_render_scientist.get_texture_coords()
                timer.log_lap(timer.lap(), "Render data")
                self._renderer_device.draw_face(shape3D, faceTex, faceCords)
                timer.log_lap(timer.lap(), "Render")
                grid = self._renderer_device.data_on_grid()
                timer.log_lap(timer.lap(), "Grab frame")
                rendered_img = self._current_render_scientist.render(grid)
                timer.log_lap(timer.lap(), "Adapt frame")

                # blending of the rendered face with the image
                mask = np.copy(rendered_img[:, :, 0])

                camera_img = ImageProcessing.optimizedBlend(rendered_img, camera_img, mask)
                #rendered_img = ImageProcessing.colorTransfer(camera_img, rendered_img, mask)
                timer.log_lap(timer.lap(), "Color transfer")
                #camera_img = ImageProcessing.blendImages(rendered_img, camera_img, mask)
                timer.log_lap(timer.lap(), "Blend")
                #self._renderer_device.update_grid()
                timer.log_lap(timer.lap(), "Refresh")

                #    cameraImg = cv2.resize(cameraImg, (800, 600))
        return camera_img