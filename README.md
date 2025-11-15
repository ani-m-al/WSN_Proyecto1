# Control de un Dron DJI Tello mediante ROS 2 y WhatsApp Cloud API

Este proyecto implementa un sistema desarrollado por el autor para controlar un dron DJI Tello a través de mensajes enviados desde WhatsApp. El trabajo integra ROS 2, un servidor Flask, la API de WhatsApp Cloud de Meta y varios nodos encargados de misión, telemetría, seguridad y visualización.

El objetivo principal consiste en demostrar un flujo de control remoto confiable donde un usuario autorizado envía comandos mediante WhatsApp, los cuales se convierten en una misión estructurada que el dron ejecuta bajo supervisión de telemetría y lógica de seguridad. El proyecto combina robótica, servicios web y visión artificial en un único sistema cohesivo.

---

## 1. Arquitectura del Sistema

El sistema desarrollado se compone de los siguientes elementos principales:

1. **WhatsApp Cloud API (Meta)** — Recibe los mensajes del usuario y los reenvía al Webhook configurado.
2. **Servidor Flask (Webhook)** — Procesa los mensajes entrantes, los almacena en una cola FIFO y expone el endpoint `/next` para ROS 2.
3. **Nodo MissionPlannerNode (ROS 2)** — Consulta el servidor, interpreta los mensajes como una misión y ejecuta cada paso de forma secuencial.
4. **Nodo DroneConnectorNode** — Comunica ROS 2 con el dron, envía comandos al Tello y publica telemetría.
5. **Nodo BatteryFailsafeNode** — Supervisa la batería y fuerza aterrizaje seguro si está baja.
6. **Nodo VideoViewerNode** — Visualiza el vídeo del dron en tiempo real y detecta zonas de color (verde, azul y rojo).
7. **Nodo de telemetría en terminal** — Muestra datos de forma continua (altura, batería, velocidad).

El dron se comunica por WiFi y todas las interacciones se integran mediante tópicos ROS 2.

---

## 2. Flujo General del Sistema

1. El usuario envía mensajes a un número de WhatsApp registrado.
2. Meta entrega esos mensajes al Webhook en Flask.
3. El Webhook los almacena en una cola accesible vía `/next`.
4. El nodo de misión consulta periódicamente estos mensajes.
5. Cuando el servidor indica que no hay más comandos, la misión se considera completa.
6. La misión se ejecuta paso a paso mediante timers.
7. El nodo conector envía los comandos reales al dron.
8. La telemetría y el vídeo se publican en ROS 2 para análisis y visualización.

---

## 3. Descripción de los Nodos ROS 2

### 3.1 DroneConnectorNode

Implementado para:

* Conectar físicamente con el dron DJI Tello.
* Activar el stream de vídeo.
* Publicar batería, altura, velocidad y vídeo.
* Ejecutar comandos recibidos por `/tello/command`.

### 3.2 BatteryFailsafeNode

Su función es garantizar seguridad:

* Supervisa continuamente `/tello/battery`.
* Publica `/tello/safety_status`.
* Si el nivel baja del umbral, envía el comando `land`.

### 3.3 MissionPlannerNode (nodo principal de misión)

* Consulta la cola de comandos proveniente de WhatsApp.
* Construye una misión secuencial.
* Ejecuta cada paso usando timers.
* Publica comandos al dron y espera condiciones como pausas o altura mínima.

### 3.4 VideoViewerNode

* Recibe vídeo desde `/tello/image_raw`.
* Convierte formatos de imagen.
* Detecta colores mediante umbrales HSV.
* Muestra el vídeo en directo.

### 3.5 Nodo de telemetría en terminal

* Presenta continuamente la información clave del dron.

---

## 4. Webhook de WhatsApp

Para permitir el control vía WhatsApp, el autor configuró:

* Una aplicación en Meta for Developers.
* Un número de prueba y probadores autorizados.
* Un Webhook público (ngrok).
* Validación automática mediante `hub.challenge`.

Los mensajes se almacenan en una cola FIFO y se consumen desde ROS 2.

---

## 5. Instalación y Ejecución

### 5.1 Requisitos

* ROS 2 Humble
* Python 3.8+
* OpenCV y cv_bridge
* Docker (opcional para aislar el nodo WhatsApp)
* Cuenta en Meta for Developers con WhatsApp Cloud API
* DJI Tello

### 5.2 Clonado del repositorio

```
git clone https://github.com/ani-m-al/WSN_Proyecto1/
cd WSN_Proyecto1
```

### 5.3 Compilación

```
colcon build
source install/setup.bash
```

### 5.4 Ejecución de los nodos

En terminales separadas:

```
ros2 run tello_pkg drone_connector_node
ros2 run tello_pkg battery_failsafe_node
ros2 run tello_pkg mission_planner_node
ros2 run tello_pkg video_viewer_node
ros2 run tello_pkg telemetry_bridge_node
```

Si se usa el servidor Flask:

```
python3 server/webhook.py
```

---

## 6. Motivación y Alcance

El autor desarrolló este proyecto para demostrar una integración práctica entre:

* Robótica aérea con ROS 2
* Servicios cloud modernos (Webhook)
* Control remoto mediante WhatsApp
* Procesamiento de vídeo para detección básica de color

Este trabajo permite tanto experimentación académica como extensión hacia sistemas más avanzados de teleoperación y automatización.

---

## 7. Licencia

El repositorio puede incluir la licencia especificada por el autor (MIT recomendada).




Solo indícalo.
