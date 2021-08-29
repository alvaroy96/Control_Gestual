import time

import cv2

import global_variables as var
from Código.DJITelloPy_Code.KC_AM_OP import am_functions, op_functions
from am_functions import followArUco
from kc_functions import keyboardInterrupts
from op_functions import initializeOP, followGestures
from other_functions import wifiConnect, wifiDisconnect


def mainProgram():
    # Inicialización del stream de video
    var.tello.streamon()
    var.frame_read = var.tello.get_frame_read()

    # Actualización de las variables height y width
    var.height, var.width, _ = var.frame_read.frame.shape

    # Actualización de la posición central de la cámara
    var.x_camCenter = int(var.width / 2)
    var.y_camCenter = int(var.height / 2)

    # Gestión de las interrupciones del teclado
    keyboardInterrupts()

    # Inicialización del control PID
    am_functions.initializePID()
    op_functions.initializePID()

    # Inicialización de OpenPose
    initializeOP()

    while True:
        # Refresco de la imagen (hold key)
        cv2.waitKey(1)

        # Lectura del frame de la cámara del dron
        frame = var.frame_read.frame

        # Conversión a escala de grises del frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Procesamiento y seguimiento del ArUco
        display = followArUco(frame, gray)
        # Detección de ArUco en escala de grises
        # Dibuja su posición sobre el frame RGB original

        # Procesamiento con OpenPose
        display = followGestures(display, frame)
        # Detección de personas en sobre el frame RGB original

        # Actualización y muestra del frame postprocesado
        var.captureFrame = display
        cv2.imshow('Display', display)

        # Finalización del programa
        if var.finish:
            var.recording = False  # Para la grabación, si está grabando
            var.sendMovements = False  # Para el envío de movimientos
            var.tello.send_rc_control(0, 0, 0, 0)  # Ordena al dron pararse

            if var.movementSenderThread is not None:
                while var.movementSenderThread.is_alive():  # Espera a que el senderThread finalice
                    time.sleep(0.05)

            var.tello.send_rc_control(0, 0, 0, 0)  # Ordena al dron pararse (por si el caso)

            var.kc_thread.stop()  # Para el listener del teclado
            cv2.destroyAllWindows()

            # Si está aterrizando, espera
            while var.landing:
                pass

            var.tello.end()

            break

        # Refresco de la imagen (hold key)
        cv2.waitKey(1)


if __name__ == '__main__':
    # Datos del punto de acceso
    ssid = "TelloRyze"
    password = "invictus"

    # Conexión al punto de acceso
    wifiConnect(ssid, ssid, password)

    # Conexión con el dron
    connected = False
    while connected is False:
        connected = var.tello.connect()

    # Ejecución del programa principal
    mainProgram()

    # Desconexión del punto de acceso
    wifiDisconnect()

    print("Fin del programa")
