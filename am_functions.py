import time
from math import copysign

import cv2
import numpy as np
from cv2 import aruco

import global_variables as var

# Variables para el reconocimiento del ArUco
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
arucoParameters = aruco.DetectorParameters_create()
identifier = 0  # ArUco objetivo de ID 0

# --- Variables para el control PID ---
# Constantes y variables del control PID
kp = 1
ki = 0
kd = 0

ts = 0.1  # Viene del delay en los cálculos (movementSender)

xError1 = 0
xError2 = 0
xLastVel = 0

yError1 = 0
yError2 = 0
yLastVel = 0

forwardError1 = 0
forwardError2 = 0
forwardLastVel = 0

yawError1 = 0
yawError2 = 0
yawLastVel = 0
# -------------------------------------

# Tiempo en el que se vio por última vez el ArUco
lastTime = 0


# Función para permitir el seguimiento del ArUco
def followArUco(orgFrame, processFrame):
    global lastTime

    # Detección del ArUco
    corners, ids, rejectedImgPoints = aruco.detectMarkers(processFrame, aruco_dict, parameters=arucoParameters)

    if np.all(ids is not None):
        # Se actualiza la marca temporal
        lastTime = time.time()

        # Se dibuja el ArUco objetivo. TODO: Tarea a futuro, filtrar identificadores
        index = np.where(ids == identifier)
        if index is not None:
            display = aruco.drawDetectedMarkers(orgFrame, corners)

            # Se calcula la traslación y rotación del ArUco y se dibuja su orientación
            rvec = None
            tvec = None

            try:
                rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners, 0.02, var.camera_matrix,
                                                                           var.distortion_coefficients)

                display = aruco.drawAxis(display, var.camera_matrix, var.distortion_coefficients, rvec, tvec, 0.01)
            except cv2.error:
                print("drawAxis exception")

            # Centro del ArUco
            x_sum = corners[0][0][0][0] + corners[0][0][1][0] + \
                    corners[0][0][2][0] + corners[0][0][3][0]
            y_sum = corners[0][0][0][1] + corners[0][0][1][1] + \
                    corners[0][0][2][1] + corners[0][0][3][1]
            x_arucoCenter = int(x_sum / 4)
            y_arucoCenter = int(y_sum / 4)

            # Se dibuja el centro del ArUco
            display = cv2.circle(display, (x_arucoCenter, y_arucoCenter), radius=5, color=(0, 0, 255),
                                 thickness=-1)

            if not var.stopArUco:
                if var.followObject == "ArUco":
                    # Se dibuja la línea desde el ArUco hasta el centro de la cámara
                    display = cv2.line(display, (var.x_camCenter, var.y_camCenter), (x_arucoCenter, y_arucoCenter),
                                       (0, 153, 255), 2)

                    # Control PID
                    if var.calcMovements:
                        controlPID_ArUco(x_arucoCenter, y_arucoCenter, rvec, tvec)
            else:
                var.l_r_vel_aruco = 0
                var.f_b_vel_aruco = 0
                var.u_d_vel_aruco = 0
                var.y_vel_aruco = 0
    else:
        # Si no se detecta el ArUco durante un tiempo, se cancela el movimiento por seguimiento
        if var.calcMovements:
            newTime = time.time()

            if (newTime - lastTime) > 1.5:
                var.l_r_vel_aruco = 0
                var.u_d_vel_aruco = 0
                var.f_b_vel_aruco = 0
                var.y_vel_aruco = 0

        # Se devuelve el frame original
        display = orgFrame

    return display


def controlPID_ArUco(x_arucoCenter, y_arucoCenter, rvec, tvec):
    global xError1, xError2, xLastVel, yError1, yError2, yLastVel, forwardError1, \
        forwardError2, forwardLastVel, yawError1, yawError2, yawLastVel

    # Cálculo del error en la velocidad
    xDif = x_arucoCenter - var.x_camCenter  # Error en píxeles
    yDif = y_arucoCenter - var.y_camCenter  # Error en píxeles
    forwardDif = tvec[0][0][2] - 0.2  # TODO: ¿Qué significa este valor?

    xError = xDif / (var.width / 2) * var.am_speed  # Error de velocidad. Eje X
    yError = yDif / (var.height / 2) * var.am_speed  # Error de velocidad. Eje Y
    forwardError = forwardDif * 10 * var.am_speed  # Error de velocidad. Proximidad

    # Resultado del control PID
    xVel = xLastVel + (var.am_q0 * xError + var.am_q1 * xError1 + var.am_q2 * xError2)
    yVel = yLastVel + (var.am_q0 * yError + var.am_q1 * yError1 + var.am_q2 * yError2)
    forwardVel = forwardLastVel + (var.am_q0 * forwardError + var.am_q1 * forwardError1 + var.am_q2 * forwardError2)

    # Actualización de errores
    xError2 = xError1
    xError1 = xError
    xLastVel = xVel

    yError2 = yError1
    yError1 = yError
    yLastVel = yVel

    forwardError2 = forwardError1
    forwardError1 = forwardError
    forwardLastVel = forwardVel

    # Limitación de velocidad
    if abs(xVel) > var.am_speed:
        xVel = copysign(var.am_speed, xVel)
    if abs(yVel) > var.am_speed:
        yVel = copysign(var.am_speed, yVel)
    if abs(forwardVel) > var.am_speed:
        forwardVel = copysign(var.am_speed, forwardVel)

    # Asignación de la velocidad para error de proximidad
    var.f_b_vel_aruco = int(forwardVel)

    # TODO: Inicialización del yawError
    # yawError = 0

    # Cálculo de los movimientos para el seguimiento del ArUco
    # Asignación de velocidades en eje X e Y (movimiento vertical y horizontal respecto a la cámara)
    var.l_r_vel_aruco = int(xVel)
    var.u_d_vel_aruco = int(-yVel)

    # TODO: Rotación (yaw) para ajustar la orientación del dron
    '''if not ((var.width / 3) < x_arucoCenter < (var.width * 2 / 3)):
        if rvec is not None and rvec.shape == (1, 1, 3):
            rmatrix = np.zeros(shape=(3, 3))
            cv2.Rodrigues(rvec, rmatrix)  # Extracción de la matriz de rotación
            rmatrix = rmatrix.transpose()  # La inversa es la traspuesta

            # Cálculos para el controlador PD
            # P = 1/4 y D = 1
            yawError = -1 * np.arctan2(rmatrix[2][0], rmatrix[2][1])

            # TODO: Ajustar multiplicador (10)
            yawSpeedDifference = 10 * (yawError / 4 + 1 * (yawError - yawLastError))  # Se multiplica por 10

            # Limitación de velocidad
            if abs(yawSpeedDifference) > var.am_speed:
                yawSpeedDifference = copysign(var.am_speed, yawSpeedDifference)

            # TODO: Asignación de la velocidad del yaw
            #var.y_vel_aruco = int(yawSpeedDifference)
            #var.y_vel_aruco = int(xSpeedDifference)
            #print(var.y_vel_aruco)'''


def initializePID():
    var.am_q0 = kp + (ki * ts) / 2 + kd / ts
    var.am_q1 = -kp + (ki * ts) / 2 - (2 * kd) / ts
    var.am_q2 = kd / ts
