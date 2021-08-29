import argparse
import os
import sys
from math import pi, atan2, degrees, copysign
from sys import platform
from threading import Thread

import cv2
import numpy as np

import global_variables as var
import time

# Variables para OpenPose y reconocimiento de gestos
from Código.DJITelloPy_Code.KC_AM_OP.other_functions import movementSender, flyAction

body_kp_id_to_name = {
    0: "Nose",
    1: "Neck",
    2: "RShoulder",
    3: "RElbow",
    4: "RWrist",
    5: "LShoulder",
    6: "LElbow",
    7: "LWrist",
    8: "MidHip",
    9: "RHip",
    10: "RKnee",
    11: "RAnkle",
    12: "LHip",
    13: "LKnee",
    14: "LAnkle",
    15: "REye",
    16: "LEye",
    17: "REar",
    18: "LEar",
    19: "LBigToe",
    20: "LSmallToe",
    21: "LHeel",
    22: "RBigToe",
    23: "RSmallToe",
    24: "RHeel",
    25: "Background"}

body_kp_name_to_id = {v: k for k, v in body_kp_id_to_name.items()}

opWrapper = None
datum = None
vectorDatum = None

pose_timestamp = (None, None)

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


# Función extraida de tello-openpose (geaxgx) - Modificada
# https://github.com/geaxgx/tello-openpose/
def get_body_kp(kp_name="Nose", person_idx=0):
    """
        Return the coordinates of a keypoint named 'kp_name' of the person of index 'person_idx' (from 0), or None if keypoint not detected
    """

    try:
        kps = datum.poseKeypoints[person_idx]
    except:
        print(f"get_body_kp: invalid person_idx '{person_idx}'")
        return None

    try:
        x, y, conf = kps[body_kp_name_to_id[kp_name]]
    except:
        print(f"get_body_kp: invalid kp_name '{kp_name}'")
        return None

    if x or y:
        return int(x), int(y)
    else:
        return None


# Función extraida de tello-openpose (geaxgx)
# https://github.com/geaxgx/tello-openpose/
def distance(p1, p2):
    """
        Distance between p1(x1,y1) and p2(x2,y2)
    """
    return np.linalg.norm(np.array(p1) - np.array(p2))


# Función extraida de tello-openpose (geaxgx)
# https://github.com/geaxgx/tello-openpose/
def vertical_angle(A, B):
    """
        Calculate the angle between segment(A,B) and vertical axe
    """
    if A is None or B is None:
        return None
    return degrees(atan2(B[1] - A[1], B[0] - A[0]) - pi / 2)


def checkTimestamp(pose, detectTime):
    global pose_timestamp

    resPose = None
    newTime = time.time()

    if pose_timestamp[1] == pose:
        if (newTime - pose_timestamp[0]) >= detectTime:
            resPose = pose
    else:
        pose_timestamp = (newTime, pose)

    return resPose


def checkPose():
    global pose_timestamp

    pose = None

    r_wrist = get_body_kp("RWrist")
    l_wrist = get_body_kp("LWrist")
    r_elbow = get_body_kp("RElbow")
    r_shoulder = get_body_kp("RShoulder")

    vert_angle_right_forearm = vertical_angle(r_wrist, r_elbow)
    vert_angle_right_arm = vertical_angle(r_elbow, r_shoulder)

    if vert_angle_right_forearm is not None and \
            vert_angle_right_arm is not None:
        # Brazo derecho "estirado" (en torno a 90 grados respecto al eje vertical)
        if 60 < abs(vert_angle_right_arm) < 120:
            # Antebrazo derecho estirado (90 grados...): Seguimiento del brazo
            if 70 < abs(vert_angle_right_forearm) < 100:
                pose = checkTimestamp("RIGHT_ARM_FOLLOW", 0.5)

            # Antebrazo derecho hacia arriba (0 grados): Cancela el movimiento del ArUco
            elif -15 < vert_angle_right_forearm < 15:
                pose = checkTimestamp("RIGHT_ARM_STOP", 0.5)

            # Antebrazo derecho hacia abajo (-180 grados): Reanuda el movimiento del ArUco
            elif -195 < vert_angle_right_forearm < -165:
                pose = checkTimestamp("RIGHT_ARM_RESUME", 0.5)

    if l_wrist is not None:
        if (var.x_camCenter - 30 < l_wrist[0] < var.x_camCenter + 30) and \
                (var.y_camCenter - 30 < l_wrist[1] < var.y_camCenter + 30):
            # Sin volar + Muñeca frente a la cámara: Orden de despegue
            if not var.tello.is_flying:
                pose = checkTimestamp("TAKE_OFF", 2)

            # Volando + Muñeca frente a la cámara: Orden de aterrizaje
            elif var.tello.is_flying:
                pose = checkTimestamp("LAND", 2)

    return pose


def initializeOP():
    global opWrapper, datum, vectorDatum

    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            # Windows Import
            if platform == "win32":
                # TODO: Parametrizar
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(dir_path + '/../../../openpose/build/python/openpose/Release')
                os.environ['PATH'] = os.environ['PATH'] + ';' + \
                                     dir_path + '/../../../openpose/build/x64/Release;' + \
                                     dir_path + '/../../../openpose/build/bin;'
                import pyopenpose as op
            else:
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append('../../python')
                # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the
                # OpenPose/python module from there. This will install OpenPose and the python library at your
                # desired installation path. Ensure that this is in your python path in order to use it.
                # sys.path.append('/usr/local/python')
                from openpose import pyopenpose as op
        except ImportError as e:
            print(
                'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this '
                'Python script in the right folder?')
            raise e

        # Flags
        parser = argparse.ArgumentParser()
        parser.add_argument("--net_resolution", default="-1x128")
        args = parser.parse_known_args()

        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()
        # TODO: Parametrizar
        params["model_folder"] = "../../../openpose/models/"
        # params["face"] = True
        # params["hand"] = True
        params["disable_blending"] = True  # Desactiva la mezcla de imágenes (salida + entrada)
        params["net_resolution"] = args[0].net_resolution

        # Starting OpenPose
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()

        # Process Image
        datum = op.Datum()
        vectorDatum = op.VectorDatum([datum])
    except Exception as e:
        print(e)


def followGestures(orgFrame, processFrame):
    datum.cvInputData = processFrame
    opWrapper.emplaceAndPop(vectorDatum)
    display = cv2.bitwise_or(orgFrame, datum.cvOutputData)

    if datum.poseKeypoints is not None:
        pose = checkPose()
        cv2.putText(display, pose, (int(var.width * 2 / 3), var.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), thickness=3)

        # TODO: Difícil de hacer con diccionario (display en follow)
        if pose == "RIGHT_ARM_FOLLOW":
            # Cambia el objeto a seguir
            var.followObject = "OP_Hand"

            # Posición del keypoint asociado a la mano
            r_wrist = get_body_kp("RWrist")
            x_handPos = r_wrist[0]
            y_handPos = r_wrist[1]

            # Se dibuja la línea desde la mano hasta el centro de la cámara
            display = cv2.line(display, (var.x_camCenter, var.y_camCenter), (x_handPos, y_handPos),
                               (0, 153, 255), 2)

            if var.calcMovements:
                # Control PID
                controlPID_OP(x_handPos, y_handPos)

        else:
            var.followObject = "ArUco"
            var.l_r_vel_op = 0
            var.u_d_vel_op = 0
            var.f_b_vel_op = 0
            var.y_vel_op = 0

            if pose == "RIGHT_ARM_STOP":
                # Cancela el seguimiento del ArUco
                var.stopArUco = True

            elif pose == "RIGHT_ARM_RESUME":
                # Reanuda el seguimiento del ArUco
                var.stopArUco = False

            elif pose == "TAKE_OFF":
                if not var.takingoff:
                    bateria = var.tello.get_battery()

                    if bateria > var.minBattery:
                        # Permite el envío de órdenes de movimiento
                        var.sendMovements = True

                        # Envío periódico de órdenes de movimiento
                        var.movementSenderThread = Thread(target=movementSender, daemon=True)
                        var.movementSenderThread.start()

                        # Orden de despegue (no bloqueante)
                        takeoffThread = Thread(target=flyAction, args=('takeoff',), daemon=True)
                        takeoffThread.start()
                    else:
                        print("Batería insuficiente para el despegue: " + str(bateria) + "%")

            elif pose == "LAND":
                if not var.landing:
                    # Cancela el envío de órdenes de movimiento
                    var.sendMovements = False

                    # Ordena al dron cancelar los movimientos
                    var.tello.send_rc_control(0, 0, 0, 0)

                    # Espera a que el senderThread finalice
                    while var.movementSenderThread.is_alive():
                        time.sleep(0.05)

                    # Ordena al dron cancelar los movimientos (por si el caso)
                    var.tello.send_rc_control(0, 0, 0, 0)

                    # Orden de aterrizaje (no bloqueante)
                    landThread = Thread(target=flyAction, args=('land',), daemon=True)
                    landThread.start()

    return display


def controlPID_OP(x_handPos, y_handPos):
    global xError1, xError2, xLastVel, yError1, yError2, yLastVel

    # Cálculo del error en la velocidad
    # P = 1/4 y D = 1
    xDif = x_handPos - var.x_camCenter  # Error en píxeles
    yDif = y_handPos - var.y_camCenter  # Error en píxeles
    # TODO: Proximidad de la mano

    xError = xDif / (var.width / 2) * var.op_speed  # Error de velocidad. Eje X
    yError = yDif / (var.height / 2) * var.op_speed  # Error de velocidad. Eje Y

    # Resultado del control PID
    xVel = xLastVel + (var.op_q0 * xError + var.op_q1 * xError1 + var.op_q2 * xError2)
    yVel = yLastVel + (var.op_q0 * yError + var.op_q1 * yError1 + var.op_q2 * yError2)

    # Actualización de errores
    xError2 = xError1
    xError1 = xError
    xLastVel = xVel

    yError2 = yError1
    yError1 = yError
    yLastVel = yVel

    # Limitación de velocidad
    if abs(xVel) > var.op_speed:
        xVel = copysign(var.op_speed, xVel)
    if abs(yVel) > var.op_speed:
        yVel = copysign(var.op_speed, yVel)

    # Cálculo de los movimientos para el seguimiento del ArUco
    # Asignación de velocidades en eje X e Y (movimiento vertical y horizontal respecto a la cámara)
    var.l_r_vel_op = int(xVel)
    var.u_d_vel_op = int(-yVel)


def initializePID():
    var.op_q0 = kp + (ki * ts) / 2 + kd / ts
    var.op_q1 = -kp + (ki * ts) / 2 - (2 * kd) / ts
    var.op_q2 = kd / ts
