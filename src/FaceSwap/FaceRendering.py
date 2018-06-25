import numpy as np


class FaceRenderer:
    def __init__(self, cam_shape, texture_img, texture_coords, renderer_device):
        self._height = cam_shape[0]
        self._width  = cam_shape[1]

        self._texture_coords = texture_coords
        self._texture_coords[0, :] /= texture_img.shape[1]
        self._texture_coords[1, :] /= texture_img.shape[0]

        self._face_texture = renderer_device.add_texture(texture_img)

    def render(self, data):
        rendered_img = np.fromstring(data, dtype=np.uint8)
        rendered_img = rendered_img.reshape((self._height, self._width, 3))
        for i in range(rendered_img.shape[2]):
            rendered_img[:, :, i] = np.flipud(rendered_img[:, :, i])

        return rendered_img

    def get_texture_coords(self):
        return self._texture_coords

    def get_face_texture(self):
        return self._face_texture
