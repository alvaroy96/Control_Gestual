import global_variables as var

# ------------------------------------------------------------
# Para la ejecución de este script es necesario estar conectado
# previamente al punto de acceso Wifi del dron
# ------------------------------------------------------------

# Datos del punto de acceso
ssid = "TelloRyze"
password = "invictus"

# Conexión con el dron
connected = False
while not connected:
    connected = var.tello.connect()

# Envío del comando para modificación del punto de acceso Wifi
var.tello.send_control_command('wifi {} {}'.format(ssid, password))
