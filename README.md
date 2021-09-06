# Control de un dron basado en visión y programación gestual

Este repositorio contiene el código implementado para la realización del Trabajo de Fin de Máster presentado por Álvaro Ayuso Martínez, alumno del Máster en Ciencia de Datos e Ingeniería de Computadores de la Universidad de Granada.

<p align="center">
	<img src="/img/3a_persona_4.jpg" height="300">
</p>

## Resumen

Este trabajo se enfoca en integrar el reconocimiento de gestos como mecanismo de control de drones y tiene su origen en el estudio de las ventajas de su aplicación en operaciones militares. Una de las principales ventajas de usar dicho mecanismo de control es la capacidad de dotar al dron de cierta autonomía respecto a su operador (unidad militar de infantería), lo que permitiría al soldado centrar en él su atención únicamente en momentos puntuales, como la puesta a punto de la unidad y el lanzamiento de órdenes mediante gestos, aprovechando el tiempo restante para realizar otras tareas. Esto es especialmente interesante en situaciones de riesgo donde la vida del soldado puede correr peligro. 

La necesidad de realizar el seguimiento del operador permite utilizar al dron, que puede situarse en una posición aérea privilegiada, para obtener una gran cantidad de información adicional del entorno de la que las unidades militares de infantería no podrían disponer debido a las limitaciones de la vista a nivel de suelo, lo que parece especialmente útil en operaciones militares en zonas urbanas.

Para la realización del trabajo, cuya aplicación resultante ha sido implementada haciendo uso del dron **Tello Ryze** y el lenguaje de programación **Python**, se propone una serie de objetivos entre los que destacan dos objetivos principales: **realizar el seguimiento automático del operador** e **implementar el control gestual del dron**. Para ello se hace uso, principalmente, de **OpenCV** como base del procesamiento de imagen, un **marcador ArUco** para la realización del seguimiento y la librería **OpenPose** para el reconocimiento de gestos.

A pesar de los problemas encontrados durante el desarrollo, los resultados obtenidos son buenos y forman una base para alcanzar aplicaciones potenciales en el campo militar, para lo cual se propone una lista de las posibles tareas que habría que realizar para profundizar y hacer más compleja la aplicación implementada.

## Contenidos

A continuación, se listan una serie de apartados básicos sobre la aplicación implementada:

- [Ejecución](#ejecución)
  * [Dependencias principales](#dependencias-principales)
  * [Lanzamiento](#lanzamiento)
- [Estudio de la implementación de la aplicación](#estudio-de-la-implementación-de-la-aplicación)
  * [global_variables.py](#global_variables.py)
  * [main.py](#main.py)
  * [kc_functions.py](#kc_functions.py)
  * [am_functions.py](#am_functions.py)
  * [op_functions.py](#op_functions.py)
  * [other_functions.py](#other_functions.py)
- [Resultados y pruebas](#resultados-y-pruebas)

## Ejecución

### Dependencias principales

La implementación del código de este repositorio se ha realizado haciendo uso de [Python 3.7.9](https://www.python.org/downloads/release/python-379/). Para su ejecución es necesario disponer, además, de las siguientes librerías:

* [DJITelloPy](https://github.com/damiafuentes/DJITelloPy) (versión 2.3.1) 
* [OpenCV-Contrib-Python](https://pypi.org/project/opencv-contrib-python/) (versión 4.5.3.56)
* [pynput](https://pypi.org/project/pynput/) (versión 1.7.3)
* [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose/)

Por otro lado, también es necesario disponer de las siguientes tecnologías para la compilación de OpenPose:

* Visual Studio 2019
* CUDA (versión 11.2.2)
* cuDNN (versión 8.1.1.33)

**Notas:** 

* La instalación de la librería DJITelloPy requiere de la instalación de OpenCV-Python. **Es imprescindible desinstalar OpenCV-Python antes de instalar OpenCV-Contrib-Python**, debido a la incompatibilidad existente entre ambas librerías.

* Para la instalación de la librería OpenPose **hay que realizar su compilación**. Se pueden encontrar todos los pasos para ello [aquí](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#compiling-and-running-openpose-from-source).

* El uso de otras versiones diferentes a las especificadas para cada una de las librerías podría alterar el correcto funcionamiento del código, especialmente para la librería DJITelloPy y las tecnologías necesarias para la compilación de OpenPose.

### Lanzamiento 

En este repositorio existen dos códigos ejecutables:

* El fichero **main.py** es, como dice su nombre, el ejecutable principal de la aplicación. 
* El fichero **modifyWifi.py** es independiente del fichero anterior, y su ejecución realiza la configuración necesaria del dron Tello Ryze de forma previa al lanzamiento del código principal de la aplicación.

Para el lanzamiento completo de la aplicación se recomiendan los siguientes pasos:

1. (Opcional) Modificar los valores correspondientes al SSID y al password en el fichero modifyWifi.py.

2. (Opcional) Encender el dron Tello Ryze y conectar manualmente al punto de acceso WiFi del dron. Si no se conoce el nombre del punto de acceso o no se dispone de la contraseña de acceso, se recomienda restablecer dichos valores mediante un reset del dron. Esto se puede conseguir pulsando durante 5 segundos el botón de encendido del dron. Tras esto, será posible acceder al punto de acceso WiFi sin contraseña.

3. (Opcional) Ejecutar el programa modifyWifi.py:

```diff
python3 modifyWifi.py
```

4. (Opcional) El dron debería haberse reiniciado. Si no ha vuelto a iniciarse el punto de acceso WiFi, hay que encenderlo de nuevo y volverse a conectar al punto de acceso (mediante las nuevas credenciales).

5. (Opcional) Modificar los valores correspondientes al SSID y al password en el fichero main.py, definidos en las primeras líneas de la función main de entrada.

6. Una vez los valores de SSID y password del programa main.py se corresponden con los del punto de acceso WiFi del dron, se puede proceder a ejecutar dicho programa:

```diff
python3 main.py
```

## Estudio de la implementación de la aplicación

En este apartado se ofrecen algunos detalles de la implementación de la aplicación. En primer lugar, conviene hacer un breve resumen de la estructura del código:

* **global_variables.py** -> Como su propio nombre indica, en este fichero se recoge la inicialización de una gran cantidad de variables globales utilizadas en los distintos ficheros. Dichas variables se inicializan antes de ejecutar el código del fichero main.py.

* **main.py** -> Realiza la conexión automática con el punto de acceso WiFi del dron y ejecuta todo el código de inicialización. Además, se encarga de obtener el streaming de vídeo del dron para comenzar a procesar todos los frames mediante llamadas a funciones del resto de ficheros de código.

* **kc_functions.py** -> Define todas las funciones y variables locales relacionadas con el controlador por teclado del dron.

* **am_functions.py** -> Define todas las funciones y variables locales relacionadas con el seguimiento automático del dron.

* **op_functions.py** -> Define todas las funciones y variables locales relacionadas con el control gestual del dron.

* **other_functions.py** -> Define otras funciones de utilidad para el funcionamiento del programa.

### global_variables.py

Este fichero incluye variables para:

* Inicializar el objeto de control del Tello Ryze, calibrar la cámara del mismo y otras variables de control para el despegue y el aterrizaje.

* Control y datos de la grabación de vídeo.

* Control y datos para el cálculo de los movimientos.

* Control y datos para el almacenamiento de los valores de velocidad para el control manual, el seguimiento automático y el control gestual, además de 6 constantes (3 para el seguimiento automático y 3 para el control gestual) para el control PID.

* Control de fin de programa.

### main.py

Conviene destacar que, dentro del bucle encargado del procesamiento de los frames, se hacen las **llamadas a las funciones encargadas del procesamiento de imagen** para el seguimiento automático (función **followArUco**) y el control gestual (función **followGestures**), además de mostrar por pantalla la imagen resultante de dicho procesamiento. También se gestiona el fin del programa.

### kc_functions.py

En primer lugar se define la función **sendMovement**, que permite el envío básico de una orden de movimiento al dron con los valores actuales de velocidad para cada una de los tres bloques principales (control manual, seguimiento automático y control gestual). 

La función **keyboardInterrupts** se encarga de lanzar un hilo que gestionará las interrupciones de teclado para actualizar los valores de las velocidades correspondientes al control manual para posteriormente enviar una orden de movimiento con las velocidades actuales. Dichas velocidades adquieren un valor fijo cuando se pulsa o mantiene pulsada una tecla de movimiento (A, W, S, D, up, down, left, right) y se anulan cuando se suelta la tecla correspondiente. Otras teclas de interés son R, que permite alternar la grabación de vídeo, la tecla Control izquierdo que permite realizar el aterrizaje sin finalizar el programa y la tecla Q que permite la finalización del programa (aterrizando el dron si se encontraba volando).

### am_functions.py

En este fichero se definen otras variables locales para la detección del marcador ArUco y el control PID para el cálculo de las velocidades de este bloque. Se define una última variable para mantener las velocidades del seguimiento automático durante un breve periodo de tiempo.

La función **followArUco** se encarga de detectar y dibujar el marcador ArUco en el frame de entrada, así como el cálculo de su centro y de las velocidades necesarias para llevar al dron a la posición de consigna (que es el centro del frame, con una cierta distancia de proximidad fijada).

La función **controlPID_aruco** incluye toda la implementación del control PID. Las velocidades calculadas por dicho control PID se ven limitadas superiormente por el valor de la variable global am_speed, para evitar velocidades mayores a las deseadas para el seguimiento automático.

La función **initializePID** sirve para inicializar los valores de las variables globales del control PID de este bloque, y se llama en el código main.py antes del bucle de procesamiento de los frames como parte de toda la inicialización del código.

### op_functions.py

En este fichero se definen otras variables locales para la definición textual de los keypoints devueltos por OpenPose, la definición de objetos utilizados por OpenPose, un timestamp (par de valores tiempo y pose) utilizado para fijar un tiempo mínimo para el reconocimiento de gestos y el control PID para el cálculo de las velocidades de este bloque.

La función **get_body_kp** permite obtener las coordenadas de un keypoint pasándole como parámetro el nombre asociado a dicho keypoint, definido previamente en las variables locales.

Las funciones **distance** y vertical_angle** calculan la distancia entre dos puntos y el ángulo de un segmento respecto el eje vertical, respectivamente. Tanto estas dos funciones como la función anterior se han extraído de la aplicación [tello-openpose](https://github.com/geaxgx/tello-openpose/).

La función **checkTimestamp** funciona de la siguiente forma:
* Si la pose del timestamp **no se corresponde** con la pose detectada en el frame actual, se actualiza el timestamp con el tiempo actual y la pose actual.
* Si la pose del timestamp **se corresponde con** la pose detectada en el frame actual y la diferencia entre el tiempo actual y el tiempo en el que se detectó por primera vez la pose es mayor al tiempo de reconocimiento mínimo de gestos, se da por reconocido el gesto, devolviendo el valor de la pose.
* Nótese que la pose y el tiempo de detección son parámetros de entrada.

La función **checkPose** hace uso de la función checkTimestamp para definir el catálogo de gestos reconocibles a partir de los keypoints devueltos por OpenPose. El gesto reconocido, devuelto por la función, servirá para la ejecución de la orden asociada a dicho gesto.

La función **initializeOP** se encarga de importar e inicializar la librería OpenPose previamente compilada, así como configurar los parámetros de uso de la misma. 

La función **followGestures** hace uso de la librería OpenPose previamente importada para la detección de poses, y posteriormente define todo el conjunto de acciones posibles, cada una de ellas asociada a una de las poses definidas en la función checkPose. En este punto se usa el valor devuelto por la función checkPose para comprobar la acción a ejecutar y posteriormente realizar su lanzamiento. Esta función también dibuja los resultados de OpenPose y la ejecución de las acciones sobre el frame de entrada.

La función **controlPID_OP** incluye toda la implementación del control PID. Las velocidades calculadas por dicho control PID se ven limitadas superiormente por el valor de la variable global op_speed, para evitar velocidades mayores a las deseadas para el control gestual.

La función **initializePID** sirve para inicializar los valores de las variables globales del control PID de este bloque, y se llama en el código main.py antes del bucle de procesamiento de los frames como parte de toda la inicialización del código.

### other_functions.py

En este fichero se definen funciones de diversa utilidad y que no se pueden clasificar en ninguno de los otros ficheros.

La función **videoCapture** se encarga de abrir un fichero de vídeo para posteriormente almacenar el frame actual, representado por la variable captureFrame. Dicha función se llama mediante la creación de un nuevo hilo al pulsar la tecla R, asociada a la grabación en el controlador por teclado. Cuando se vuelve a pulsar R, la variable recording se desactiva y así el hilo dedicado a la grabación de vídeo finaliza su ejecución.

La función **movementSender** se encarga de lanzar una orden de movimiento cada 100 ms, además de gestionar los tiempos para el cálculo de velocidades y así optimizar el rendimiento de la aplicación. Esta función es imprescindible para el seguimiento automático y el control gestual, que no proveen de otro mecanismo para el envío de órdenes.

La función **flyAction** se definió para gestionar el despegue y el aterrizaje en un hilo independiente del hilo de ejecución principal, puesto que las llamadas a los comandos de DJITelloPy utilizados son bloqueantes. También se actualizan los valores de las variables takingoff y landing, que son de utilidad en otros lugares del código de la aplicación.

Las funciones **wifiConnect** y **wifiDisconnect** se definen para la automatización de la conexión del sistema al punto de acceso habilitado por el dron. La primera parte de la función wifiConnect se dedica a la comprobación de que la configuración actual se corresponde con los valores SSID y password introducidos en el fichero main.py. En caso contrario, puede crear o modificar el fichero de configuración. Posteriormente, cuando la configuración es correcta, se realiza la conexión automática al punto de acceso haciendo uso de las herramientas netsh (para conectarse al punto de acceso) y ping (para comprobar que efectivamente hay conexión con el dron. En caso contrario, sigue intentándolo).

## Resultados y pruebas

A continuación se muestran algunas imágenes en las que se puede apreciar el catálogo de gestos actualmente definido. Dichas imágenes han sido extraídas de uno de los vídeos de prueba sobre la aplicación implementada para la elaboración de la documentación y la presentación de este Trabajo de Fin de Máster.

<p align="center">
	<img src="/img/prueba_completa_0.jpg" height="200">
	<img src="/img/prueba_completa_1.jpg" height="200">
</p>
<p align="center">
	<img src="/img/prueba_completa_2.jpg" height="200">
	<img src="/img/prueba_completa_3.jpg" height="200">
</p>
<p align="center">
	<img src="/img/prueba_completa_4.jpg" height="200">
	<img src="/img/prueba_completa_5.jpg" height="200">
</p>
<p align="center">
	<img src="/img/prueba_completa_6.jpg" height="200">
</p>