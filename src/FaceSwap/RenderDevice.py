import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class RenderDevice:
    def __init__(self, width, height, mesh):
        self._width = width
        self._height = height

        glutInit()
        glutInitWindowSize(self._width, self._height)
        glutCreateWindow("Drawmask")
        glutInitDisplayMode(GLUT_DOUBLE)
        #glutDisplayFunc(self.draw_face)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glColor3f(0.0, 0.0, 0.0)

        self._set_ortho()

        self._mesh = mesh

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

    #Drawing
    def draw_face(self, vertices, face_texture, texture_coords):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindTexture(GL_TEXTURE_2D, face_texture)

        vertex_coords = vertices.flatten('F')
        tex_coords = texture_coords.flatten('F')
        indices = self._mesh.flatten()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, vertex_coords)
        glTexCoordPointer(2, GL_FLOAT, 0, tex_coords)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glFlush()

    #Get screen data
    def data_on_grid(self):
        pixels = glReadPixels(0, 0, self._width, self._height, GL_BGR, GL_UNSIGNED_BYTE)
        return pixels

    def update_grid(self):
        glutSwapBuffers()

    def add_texture(self, img):

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.shape[1], img.shape[0], 0, GL_BGR, GL_UNSIGNED_BYTE, img)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        return texture_id

    def _set_ortho(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self._width, self._height, 0, -1000, 1000)
        glMatrixMode(GL_MODELVIEW)

