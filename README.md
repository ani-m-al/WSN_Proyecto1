# Sistema Integrado de Control para Dron DJI Tello con ROS 2 y Extensión vía WhatsApp Cloud API

Este proyecto implementa un sistema completo desarrollado por el autor para operar un dron DJI Tello utilizando ROS 2. El sistema conforma una arquitectura modular que integra control de vuelo, telemetría, seguridad por batería, planificación automática de misiones, procesamiento de vídeo y, como extensión opcional, control remoto mediante mensajes enviados desde WhatsApp.

El objetivo principal del proyecto es crear un entorno funcional y demostrativo donde múltiples nodos ROS 2 colaboran para controlar, supervisar y gestionar la operación del dron. El módulo de WhatsApp amplía el sistema permitiendo introducir misiones mediante mensajería móvil, pero es únicamente una parte del ecosistema general, cuyo núcleo es la infraestructura robótica basada en ROS 2.

---

## 1. Arquitectura General del Sistema

El sistema se compone de los siguientes nodos principales:

1. **DroneConnectorNode** — Enlace directo con el dron DJI Tello.
   Se encarga de transmitir comandos, publicar telemetría y ofrecer el flujo de vídeo crudo.

2. **TelemetryBridgeNode** — Consolida información del dron y la muestra en terminal en tiempo real.

3. **BatteryFailsafeNode** — Supervisa la batería y envía aterrizaje inmediato cuando baja del umbral.

4. **MissionPlannerNode** — Ejecuta una misión completa paso a paso mediante timers y condiciones.

5. **VideoViewerNode** — Procesa vídeo del dron y detecta regiones verdes, azules y rojas usando OpenCV.

6. **WhatsApp Mission Module (Webhook + nodo)** — Módulo externo que permite construir misiones enviando mensajes desde WhatsApp.
   Es un complemento funcional al sistema principal, no un requisito.

La interconexión entre nodos se realiza mediante tópicos ROS 2. El dron se comunica vía WiFi con el nodo conector.

---

## 2. Flujo de Trabajo del Sistema

El funcionamiento integrado es el siguiente:

1. El **DroneConnectorNode** conecta con el Tello, habilita vídeo y publica telemetría.
2. El **TelemetryBridgeNode** muestra altura, batería y velocidad en la terminal.
3. El **BatteryFailsafeNode** publica un estado de seguridad y fuerza aterrizaje si la batería baja del límite.
4. El **MissionPlannerNode** ejecuta una misión automática (secuencia de takeoff, esperas, movimientos, etc.).
5. El **VideoViewerNode** muestra el vídeo y detecta colores en tiempo real.
6. Opcionalmente, un usuario puede enviar comandos por WhatsApp:
   el Webhook recibe los mensajes, los almacena en una cola y el nodo de misión los convierte en pasos de vuelo.

---

## 3. Descripción de los Nodos ROS 2

### 3.1 DroneConnectorNode

Nodo principal de comunicación con el dron.
Funciones clave:

* Conexión y manejo del dron DJI Tello mediante `djitellopy`.
* Publicación de:

  * `/tello/image_raw`
  * `/tello/battery`
  * `/tello/speed_x`
  * `/tello/height`
* Ejecución de comandos recibidos por `/tello/command`.

---

### 3.2 TelemetryBridgeNode

Nodo dedicado a monitoreo local.
Funciones:

* Recibe telemetría en tiempo real.
* Muestra estado del dron en un panel de consola.
* Permite supervisar el vuelo sin interfaz gráfica.

---

### 3.3 BatteryFailsafeNode

Módulo de seguridad obligatorio.
Funciones:

* Supervisa `/tello/battery`.
* Publica `/tello/safety_status`.
* En caso de batería baja, envía `land` y evita seguir misiones.

---

### 3.4 MissionPlannerNode

Controlador secuencial de misiones.
Características:

* Ejecuta una lista ordenada de comandos: delays, movimientos, esperas.
* Emplea timers como mecanismo de máquina de estados.
* Depende del estado de seguridad publicado por el failsafe.

---

### 3.5 VideoViewerNode (Procesador de Cámara)

Procesamiento de vídeo en tiempo real.
Funciones:

* Conversión segura de formatos ROS a BGR.
* Detección de colores verde, azul y rojo mediante HSV.
* Visualización en ventana OpenCV.

---

### 3.6 Módulo de WhatsApp (opcional pero destacado)

Extensión desarrollada por el autor para controlar misiones vía mensajería móvil.
Flujo:

1. WhatsApp → Meta → Webhook Flask.
2. Webhook → Cola FIFO accesible vía `/next`.
3. MissionPlannerNode extrae comandos y construye la misión.
4. El dron ejecuta la misión como si fuera una misión local estándar.

Este módulo no sustituye el control ROS 2, sino que lo complementa de forma remota.

---

## 4. Instalación y Uso

### Requisitos

* ROS 2 Humble
* Python 3.8+
* OpenCV + cv_bridge
* DJI Tello
* (Opcional) Meta for Developers + WhatsApp Cloud API
* (Opcional) Docker para ejecutar el webhook

### Clonado del repositorio

```
git clone https://github.com/ani-m-al/WSN_Proyecto1/
cd WSN_Proyecto1
```

### Compilación

```
colcon build
source install/setup.bash
```

### Ejecución de los nodos principales

```
ros2 run tello_pkg drone_connector_node
ros2 run tello_pkg telemetry_bridge_node
ros2 run tello_pkg battery_failsafe_node
ros2 run tello_pkg mission_planner_node
ros2 run tello_pkg video_viewer_node
```

### Servidor WhatsApp (opcional)

```
python3 server/webhook.py
```

---

## 5. Alcance del Proyecto

Este trabajo demuestra una integración completa entre:

* Robótica aérea (DJI Tello + ROS 2)
* Comunicación entre nodos ROS 2
* Seguridad en vuelo mediante failsafe
* Procesamiento visual
* Automatización de misiones
* Control remoto ampliado vía WhatsApp

Se trata de un sistema extensible y modular pensado para investigación, docencia y experimentación con robótica conectada a servicios cloud.

---
* Un diagrama ASCII o Mermaid para la arquitectura,
* O una versión bilingüe español/inglés.
