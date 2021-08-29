import os
import time
from xml.dom import minidom

import cv2

import global_variables as var


# Función que se encarga de la grabación de video
def videoCapture():
    fps = var.tello.cap.get(cv2.CAP_PROP_FPS)
    output = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'MP4V'), fps, (var.width, var.height))

    while var.recording:
        output.write(var.captureFrame)
        time.sleep(0.001)

    output.release()


# Función para enviar periódicamente las órdenes de movimiento en base al ArUco y a los gestos
def movementSender():
    while var.sendMovements:
        var.tello.send_rc_control(var.l_r_vel_keyboard + var.l_r_vel_aruco + var.l_r_vel_op,
                                  var.f_b_vel_keyboard + var.f_b_vel_aruco + var.f_b_vel_op,
                                  var.u_d_vel_keyboard + var.u_d_vel_aruco + var.u_d_vel_op,
                                  var.y_vel_keyboard + var.y_vel_aruco + var.y_vel_op)

        var.calcMovements = False
        time.sleep(0.099)
        var.calcMovements = True
        time.sleep(0.001)


# Función que gestiona las variables takingoff y landing
def flyAction(mode):
    response = None

    if mode == 'takeoff':
        var.takingoff = True
        response = var.tello.takeoff()

        if var.tello.is_flying:
            var.takingoff = False

        else:
            var.tello.land()

    elif mode == 'land':
        var.landing = True
        response = var.tello.land()

        if not var.tello.is_flying:
            var.landing = False

    return response


def wifiConnect(name, ssid, password):
    # Comprobación del fichero XML y creación de la conexión
    if password is not "":
        if os.path.isfile("networks/" + name + ".xml"):
            xml = minidom.parse("networks/" + name + ".xml")
            elementPwd = xml.getElementsByTagName("keyMaterial")[0].firstChild
            pwd = elementPwd.data

            if pwd != password:
                elementPwd.data = password

                command = "netsh wlan add profile filename=\"" + "networks/" + name + ".xml\"" + " interface=Wi-Fi"
                with open("networks/" + name + ".xml", 'w') as file:
                    # Indentation-Newline-Encoding
                    xml.writexml(file, addindent='  ', encoding='utf-8')
                    print("Fichero de red modificado")
                os.system(command)
        else:
            if not os.path.isfile("networks/"):
                os.mkdir("networks/")

            config = """<?xml version=\"1.0\"?>
            <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                <name>""" + name + """</name>
                <SSIDConfig>
                    <SSID>
                        <name>""" + ssid + """</name>
                    </SSID>
                </SSIDConfig>
                <connectionType>ESS</connectionType>
                <connectionMode>auto</connectionMode>
                <MSM>
                    <security>
                        <authEncryption>
                            <authentication>WPA2PSK</authentication>
                            <encryption>AES</encryption>
                            <useOneX>false</useOneX>
                        </authEncryption>
                        <sharedKey>
                            <keyType>passPhrase</keyType>
                            <protected>false</protected>
                            <keyMaterial>""" + password + """</keyMaterial>
                        </sharedKey>
                    </security>
                </MSM>
            </WLANProfile>"""
            command = "netsh wlan add profile filename=\"" + "networks/" + name + ".xml\"" + " interface=Wi-Fi"
            with open("networks/" + name + ".xml", 'w') as file:
                file.write(config)
                print("Fichero de red creado")
            os.system(command)

    # Conexión a la red
    response = 1
    while response != 0:
        command = "netsh wlan connect name=\"" + name + "\" ssid=\"" + ssid + "\" interface=Wi-Fi"
        os.system(command)

        time.sleep(1)
        response = os.system("ping -n 1 192.168.10.1")

        time.sleep(1)


def wifiDisconnect():
    command = "netsh wlan disconnect interface=Wi-Fi"
    os.system(command)
