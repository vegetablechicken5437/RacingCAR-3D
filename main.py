import os
import sys
from math import *
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from objloader import OBJ

def loadPathCoords(filename):
    f = open(filename, mode='r')
    data = []
    line = f.readline()
    line = line.split()
    for i in range(len(line)):
        line[i] = float(line[i]) 
    while line:
        data.append(line)
        line = f.readline()
        line = line.split()
        for i in range(len(line)):
            line[i] = float(line[i])    
    f.close()
    return data

windowWidth = 800
windowHeight = 600

PATH = 'RacingCAR/Path.txt'
SG_Car = 'RacingCAR/SG_Car.obj'
FullTrack = 'RacingCAR/FullTrack.obj'
pathCoords = np.array(loadPathCoords(PATH))
index = -1
t = 50

def inverse(A):
    A = np.array(A)
    inv_A = np.linalg.inv(A)
    return inv_A

def norm(v):
    length = (v[0]**2 + v[1]**2 + v[2]**2)**0.5
    for i in range(3):
        v[i]/=length
    return v

def getTransformMatrix(i):
    E, A, U, u, v, w = [], [], np.array([0,0,1]), [], [], []
    for j in range(3):
        E.append(pathCoords[i][j])
        A.append(pathCoords[i+1][j])
        w.append(E[j]-A[j])
    w = np.array(norm(w))
    u = norm(np.cross(U, w))
    v = np.cross(w, u)

    for j in range(3):       
        E[j] += u[j]*4.5 

    M = np.array([[u[0], w[0], v[0], E[0]],
                  [u[1], w[1], v[1], E[1]],
                  [u[2], w[2], v[2], E[2]],
                  [   0,    0,    0,    1]])
    M = np.transpose(M)
    matrices = [M, E, A, u, v, w]
    return matrices

def setCamera(index, mode=0):
    matrices = getTransformMatrix(index)
    E, A, u, v, w = matrices[1], matrices[2], matrices[3], matrices[4], matrices[5]
    eye, center = [], []
    if mode == 0:        
        for j in range(3):       
            eye.append(1000)
            center.append(0)
    elif mode == 1:        
        for j in range(3):       
            eye.append(E[j] + v[j]*2.5)
            center.append(A[j] + u[j]*4.5 + v[j]*2.5)
    elif mode == 2:        
        for j in range(3):       
            eye.append(E[j] + v[j]*10 + w[j]*60)
            center.append(A[j] + u[j]*4.5 + v[j]*7.5)

    gluLookAt(eye[0],eye[1],eye[2],center[0],center[1],center[2],0,0,1)
    
def drawCoordinate():
    glLineWidth(3)
    glBegin(GL_LINES)

    glColor3f(1,0,0) # red
    glVertex3f(0,0,0)
    glVertex3f(100,0,0)

    glColor3f(0,1,0) # green
    glVertex3f(0,0,0)
    glVertex3f(0,100,0)

    glColor3f(0,0,1) # blue
    glVertex3f(0,0,0)
    glVertex3f(0,0,100)
    glEnd()

def drawCar(M):
    glPushMatrix() 
    glLoadMatrixf(M)
    glScalef(0.2,0.2,0.2)
    car.render()
    glPopMatrix()

def drawTrack():  
    track.render()

def display():
    global index
    if index == len(pathCoords)-1: index = -1
    matrices = getTransformMatrix(index)
    M = matrices[0]
    
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glViewport(0, 0, windowWidth, windowHeight)
    glFrustum(-windowWidth/400,windowWidth/400,-windowHeight/400,windowHeight/400,10,4000) 
    setCamera(index, 2)
    
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)
    drawCar(M) 
    drawTrack()   
    glDisable(GL_LIGHTING)

    # drawCoordinate()
    glutSwapBuffers()

def timerFunc(value):
    global index
    index = index+1
    glutPostRedisplay()   
    glutTimerFunc(t, timerFunc, 0)
    
def reshape(width,height):
    glViewport(0, 0, width, height)
    
def keyboard( key, x, y ):
    if key == b'\x1b': #ESC
        os._exit(0)


glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_MULTISAMPLE )
glutCreateWindow(b'main')
glutReshapeWindow(windowWidth,windowHeight)
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
lightAmbient = [ 0.5,0.5,0.5,1.0 ]
lightDiffuse = [ 0.9,0.9,0.9,1.0 ]
lightSpecular = [ 1.0,1.0,1.0,1.0 ]
lightPosition = [ 1000,1000,1000,1.0 ]
glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmbient)
glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse)
glLightfv(GL_LIGHT0, GL_SPECULAR, lightSpecular)
glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
glutReshapeFunc(reshape)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutTimerFunc(t, timerFunc, 0) 
car = OBJ(SG_Car)
track = OBJ(FullTrack)
glutMainLoop()