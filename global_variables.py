import numpy as np
from djitellopy import Tello


# --- Tello ---
tello = Tello()
camera_matrix = np.array([[929.13251611, 0., 479.17562521],
                          [0., 931.26451127, 295.35871445],
                          [0., 0., 1.]])
distortion_coefficients = np.array([[1.35915086e-01, -2.23009579e+00,
                                     -1.37639118e-02, -2.29458613e-03,
                                     8.38818104e+00]])
takingoff = False
landing = False
minBattery = 25

# --- Grabación ---
frame_read = None
videoCaptureThread = None
recording = False
captureFrame = None

# --- Movimiento ---
movementSenderThread = None
sendMovements = False
calcMovements = True
followObject = "ArUco"

# Alto y ancho del frame
height = 0
width = 0

# Posición central de la cámara
x_camCenter = 0
y_camCenter = 0

# --- Control por teclado ---
kc_thread = None
pressedKeys = {'w': False, 's': False, 'a': False, 'd': False,
               'r': False, 't': False, 'up': False, 'down': False,
               'rotleft': False, 'rotright': False, 'ctrl': False}
kc_speed = 60
l_r_vel_keyboard = 0
f_b_vel_keyboard = 0
u_d_vel_keyboard = 0
y_vel_keyboard = 0

# --- ArUco ---
stopArUco = False
am_speed = 30
l_r_vel_aruco = 0
f_b_vel_aruco = 0
u_d_vel_aruco = 0
y_vel_aruco = 0

am_q0 = 0
am_q1 = 0
am_q2 = 0

# --- OpenPose ---
op_speed = 30
l_r_vel_op = 0
f_b_vel_op = 0
u_d_vel_op = 0
y_vel_op = 0

op_q0 = 0
op_q1 = 0
op_q2 = 0

# --- Fin del programa ---
finish = False
