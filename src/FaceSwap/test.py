from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import time
import random


def initFun():
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glColor3f(0.0, 0.0, 0.0)
    glPointSize(4.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, 640.0, 0.0, 480.0)


def displayFun():
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_POINTS)
    glVertex2f(100 * random.random(), 50 * random.random())
    glVertex2f(100 * random.random(), 130 * random.random())
    glVertex2f(150 * random.random(), 130 * random.random())
    glEnd()
    glFlush()
    print str(glReadPixels(0, 0, 1, 1, GL_BGR, GL_UNSIGNED_BYTE)


if __name__ == '__main__':
    glutInit()
    glutInitWindowSize(640, 480)
    glutCreateWindow("Drawdots")
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    #glutDisplayFunc(displayFun)
    initFun()
    #glutMainLoop()

    while True:
        displayFun()
        time.sleep(0.02)