import threading
import time
from threading import Thread

from pynput import keyboard

from other_functions import videoCapture, movementSender, flyAction

import global_variables as var

# Variables para el control de movimientos
left_vel = 0
right_vel = 0
forward_vel = 0
backward_vel = 0
up_vel = 0
down_vel = 0
left_yaw_vel = 0
right_yaw_vel = 0


def sendMovement():
    var.tello.send_rc_control(var.l_r_vel_keyboard + var.l_r_vel_aruco + var.l_r_vel_op,
                              var.f_b_vel_keyboard + var.f_b_vel_aruco + var.f_b_vel_op,
                              var.u_d_vel_keyboard + var.u_d_vel_aruco + var.u_d_vel_op,
                              var.y_vel_keyboard + var.y_vel_aruco + var.y_vel_op)


def keyboardInterrupts():
    def on_press(key):
        global left_vel, right_vel, forward_vel, backward_vel, up_vel, down_vel, left_yaw_vel, right_yaw_vel

        try:
            # Left
            if key.char == 'a' and not var.pressedKeys['a']:
                var.pressedKeys['a'] = True
                left_vel = -var.kc_speed
                var.l_r_vel_keyboard = left_vel + right_vel
                sendMovement()

            # Right
            elif key.char == 'd' and not var.pressedKeys['d']:
                var.pressedKeys['d'] = True
                right_vel = var.kc_speed
                var.l_r_vel_keyboard = left_vel + right_vel
                sendMovement()

            # Forward
            elif key.char == 'w' and not var.pressedKeys['w']:
                var.pressedKeys['w'] = True
                forward_vel = var.kc_speed
                var.f_b_vel_keyboard = forward_vel + backward_vel
                sendMovement()

            # Backward
            elif key.char == 's' and not var.pressedKeys['s']:
                var.pressedKeys['s'] = True
                backward_vel = -var.kc_speed
                var.f_b_vel_keyboard = forward_vel + backward_vel
                sendMovement()

            # Grabación de video
            elif key.char == 'r':
                if not var.videoCaptureThread or not var.videoCaptureThread.is_alive():
                    print("Comenzando la grabación")
                    var.recording = True
                    var.videoCaptureThread = Thread(target=videoCapture, daemon=True)
                    var.videoCaptureThread.start()
                else:
                    print("Deteniendo la grabación")
                    var.recording = False

            # Fin del programa
            elif key.char == 'q' and not var.takingoff:
                var.finish = True

        except AttributeError:
            # Up
            if key == keyboard.Key.up and not var.pressedKeys['up']:
                var.pressedKeys['up'] = True

                if not var.tello.is_flying and not var.takingoff:
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
                else:
                    up_vel = var.kc_speed
                    var.u_d_vel_keyboard = up_vel + down_vel
                    sendMovement()

            # Down
            elif key == keyboard.Key.down and not var.pressedKeys['down']:
                var.pressedKeys['down'] = True
                down_vel = -var.kc_speed
                var.u_d_vel_keyboard = up_vel + down_vel
                sendMovement()

            # Land
            elif key == keyboard.Key.ctrl_l and not var.pressedKeys['ctrl']:
                var.pressedKeys['ctrl'] = True

                if var.tello.is_flying and not var.landing:
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

            # Rotate Left
            elif key == keyboard.Key.left and not var.pressedKeys['rotleft']:
                var.pressedKeys['rotleft'] = True
                left_yaw_vel = -2 * var.kc_speed
                var.y_vel_keyboard = left_yaw_vel + right_yaw_vel
                sendMovement()

            # Rotate Right
            elif key == keyboard.Key.right and not var.pressedKeys['rotright']:
                var.pressedKeys['rotright'] = True
                right_yaw_vel = 2 * var.kc_speed
                var.y_vel_keyboard = left_yaw_vel + right_yaw_vel
                sendMovement()

        except ValueError:
            print("ValueError exception")

    def on_release(key):
        global left_vel, right_vel, forward_vel, backward_vel, up_vel, down_vel, left_yaw_vel, right_yaw_vel

        try:
            # Left
            if key.char == 'a':
                var.pressedKeys['a'] = False
                left_vel = 0
                var.l_r_vel_keyboard = left_vel + right_vel
                sendMovement()

            # Right
            elif key.char == 'd':
                var.pressedKeys['d'] = False
                right_vel = 0
                var.l_r_vel_keyboard = left_vel + right_vel
                sendMovement()

            # Forward
            elif key.char == 'w':
                var.pressedKeys['w'] = False
                forward_vel = 0
                var.f_b_vel_keyboard = forward_vel + backward_vel
                sendMovement()

            # Backward
            elif key.char == 's':
                var.pressedKeys['s'] = False
                backward_vel = 0
                var.f_b_vel_keyboard = forward_vel + backward_vel
                sendMovement()

        except AttributeError:
            # Up
            if key == keyboard.Key.up:
                var.pressedKeys['up'] = False
                if int(var.tello.get_height()) > 0:
                    up_vel = 0
                    var.u_d_vel_keyboard = up_vel + down_vel
                    sendMovement()

            # Down
            elif key == keyboard.Key.down:
                var.pressedKeys['down'] = False
                down_vel = 0
                var.u_d_vel_keyboard = up_vel + down_vel
                sendMovement()

            # Land
            elif key == keyboard.Key.ctrl_l:
                var.pressedKeys['ctrl'] = False

            # Rotate Left
            elif key == keyboard.Key.left:
                var.pressedKeys['rotleft'] = False
                left_yaw_vel = 0
                var.y_vel_keyboard = left_yaw_vel + right_yaw_vel
                sendMovement()

            # Rotate Right
            elif key == keyboard.Key.right:
                var.pressedKeys['rotright'] = False
                right_yaw_vel = 0
                var.y_vel_keyboard = left_yaw_vel + right_yaw_vel
                sendMovement()

        except ValueError:
            print("ValueError exception")

    var.kc_thread = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    var.kc_thread.start()
