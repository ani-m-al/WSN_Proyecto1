# Sistema Integrado de Control para Dron DJI Tello con ROS 2 y Extensión vía WhatsApp Cloud API

Este proyecto implementa un sistema completo para operar un dron DJI Tello utilizando ROS 2. La arquitectura desarrollada combina control de vuelo, telemetría, seguridad por batería, planificación automática de misiones, procesamiento de vídeo y, como extensión opcional, control remoto mediante WhatsApp Cloud API.

La estructura del repositorio incluye además un **Dockerfile** que permite construir una imagen ROS 2 aislada para ejecutar el módulo de WhatsApp u otros nodos que requieran entornos controlados, lo que facilita despliegues portables y reproducibles.

El objetivo del proyecto es demostrar una integración sólida entre distintos componentes robóticos y servicios externos, gestionados mediante un ecosistema modular basado en ROS 2, donde cada nodo opera una función específica y colaborativa.

---

## 1. Arquitectura General del Sistema

El sistema se compone de los siguientes nodos principales:

1. **DroneConnectorNode** — Conexión directa con el dron DJI Tello.
   Publica telemetría, vídeo y ejecuta comandos.

2. **TelemetryBridgeNode** — Monitorea variables del dron en la terminal.

3. **BatteryFailsafeNode** — Supervisa la batería y fuerza aterrizaje inmediato.

4. **MissionPlannerNode** — Ejecuta misiones secuenciales basadas en comandos y condiciones.

5. **VideoViewerNode** — Procesa vídeo en tiempo real y detecta colores con OpenCV.

6. **WhatsApp Mission Module (Webhook + Nodo en Docker)** — Interpreta comandos enviados desde WhatsApp y los convierte en pasos de vuelo.

En el repositorio se incluye un **Dockerfile preconfigurado para ROS 2**, que permite ejecutar el nodo de WhatsApp dentro de un contenedor, aislándolo del host y facilitando dependencias, despliegue y compatibilidad.

La interconexión se realiza mediante tópicos ROS 2 y el dron se comunica vía WiFi.

---

## 2. Flujo de Trabajo del Sistema

1. **DroneConnectorNode** conecta con el Tello, inicia vídeo y publica telemetría.
2. **TelemetryBridgeNode** muestra continuamente el estado del dron.
3. **BatteryFailsafeNode** determina si es seguro volar y actúa ante batería baja.
4. **MissionPlannerNode** ejecuta una misión autónoma paso por paso.
5. **VideoViewerNode** muestra vídeo y realiza detección de colores.
6. **WhatsApp Module (Docker)**:

   * Webhook → recibe mensajes desde Meta.
   * Cola FIFO → almacena comandos.
   * Nodo ROS 2 → consulta el servidor y construye la misión.

---

## 3. Descripción de los Nodos ROS 2

### 3.1 DroneConnectorNode

Control del dron mediante `djitellopy`. Publica:

* `/tello/image_raw`
* `/tello/battery`
* `/tello/speed_x`
* `/tello/height`
  Consume: `/tello/command`.

---

### 3.2 TelemetryBridgeNode

Procesa y muestra:

* batería
* velocidad
* altura

---

### 3.3 BatteryFailsafeNode

Supervisa `/tello/battery`, publica `/tello/safety_status` y envía `land` cuando es necesario.

---

### 3.4 MissionPlannerNode

Ejecuta misiones mediante una máquina de estados basada en timers y condiciones.

---

### 3.5 VideoViewerNode

Convierte imágenes a BGR, detecta colores por HSV y muestra la salida en OpenCV.

---

### 3.6 Módulo de WhatsApp (Docker + Flask Webhook)

Módulo opcional que permite introducir misiones vía WhatsApp:

1. WhatsApp → Meta → Webhook Flask
2. Webhook → Cola FIFO
3. Nodo ROS 2 en Docker → `/next` → comandos → `/tello/command`

### Dockerfile incluido en el repositorio

El repositorio contiene un **Dockerfile ROS 2 preconfigurado**, diseñado para:

* Crear una imagen ligera basada en ROS 2 Humble.
* Instalar dependencias necesarias para el nodo de WhatsApp y ejecución en contenedores.
* Permitir lanzar ROS 2 dentro de Docker sin conflictos con el entorno del host.
* Aislar el nodo de misión/WhatsApp del resto de sistemas locales.
* Ejecutar el nodo responsable de consultar mensajes y publicar comandos al dron.

El uso de Docker asegura reproducibilidad, portabilidad y un entorno controlado para la integración con servicios externos como la API de Meta.

---

## 4. Instalación y Uso

### Requisitos

* ROS 2 Humble
* Python 3.8+
* OpenCV + cv_bridge
* DJI Tello
* (Opcional) Meta for Developers + WhatsApp Cloud API
* (Opcional) **Docker** (para el nodo de WhatsApp)

---

### Clonado del repositorio

```
git clone https://github.com/ani-m-al/WSN_Proyecto1/
cd WSN_Proyecto1
```

---

### Compilación

```
colcon build
source install/setup.bash
```

---

### Ejecución de los nodos principales

```
ros2 run tello_pkg drone_connector_node
ros2 run tello_pkg telemetry_bridge_node
ros2 run tello_pkg battery_failsafe_node
ros2 run tello_pkg mission_planner_node
ros2 run tello_pkg video_viewer_node
```

---

### Uso del Dockerfile (opcional)

Construir la imagen:

```
docker build -t tello_whatsapp_img .
```

Ejecutar el contenedor:

```
docker run --network=host tello_whatsapp_img
```

Dentro del contenedor se ejecuta el nodo ROS 2 encargado de consultar mensajes del webhook.

---

### Servidor WhatsApp (opcional)

```
python3 server/webhook.py
```

---

Aquí tienes **el proceso completo, técnico, secuencial y totalmente coherente** con todo lo que desarrollaste en esta conversación. Está escrito para que quede listo para poner en tu informe o README, sin ambigüedades y con la arquitectura precisa:
**Webhook en la VM, túnel ngrok en la VM, nodo ROS 2 en Docker, y flujo WhatsApp → Meta → VM → Docker → ROS → dron Tello**.

---

# Proceso Completo para el Funcionamiento del Nodo de WhatsApp

El nodo de WhatsApp forma parte de un sistema distribuido compuesto por:

* **Máquina Física (host)**
* **Máquina Virtual Linux (VM)** con el servidor Flask y ngrok
* **Contenedor Docker** dentro de la VM con el nodo ROS 2 que consulta mensajes
* **Nodo DroneConnectorNode** en la VM
* **Dron DJI Tello**

Su propósito es permitir que el dron reciba misiones enviadas por un usuario a través de WhatsApp Cloud API, interpretando mensajes de texto como comandos válidos de vuelo.

A continuación se describe el proceso completo desde la configuración de Meta hasta la ejecución de la misión específica del nodo que integra WhatsApp.

---

# 1. Configuración en Meta for Developers

### 1.1 Crear cuenta en Meta for Developers

Ingresar a:
`https://developers.facebook.com/`
Aceptar los términos de desarrollador.

### 1.2 Crear una cuenta de negocio

Mediante Meta Business Suite:

* Crear una nueva cuenta comercial.
* Asignar responsable, nombre y correo asociado.

### 1.3 Crear una nueva aplicación

En Meta for Developers:

1. *Mis aplicaciones → Crear aplicación*
2. Seleccionar tipo: **Negocios**
3. Asociarla a la cuenta comercial creada.

### 1.4 Agregar el producto “WhatsApp”

Desde *Agregar producto* → seleccionar **WhatsApp**
Esto habilita la API de WhatsApp Cloud para la aplicación.

### 1.5 Obtener número de prueba y token de acceso

Meta proporciona:

* Número telefónico de prueba
* Token de acceso temporal
* Código de verificación para habilitar probadores

### 1.6 Registrar probadores

En la sección de configuración:

* Añadir el número personal como “probador”
* Enviar por WhatsApp el código de verificación al número de prueba
* Meta lo habilita como número autorizado

---

# 2. Configuración del Webhook en la Máquina Virtual

Todo lo relacionado con WhatsApp se maneja en la **VM**, no en la máquina física ni en Docker.

### 2.1 Crear el servidor Flask

En la VM se implementa un servidor Flask con:

* Ruta GET para validación del webhook
* Ruta POST para recibir mensajes
* Cola FIFO interna
* Endpoint REST `/next` para que ROS consulte los mensajes

El servidor:

1. Recibe cada mensaje enviado al número de WhatsApp
2. Lo inserta en la cola FIFO
3. Ofrece el siguiente mensaje pendiente vía `/next`

### 2.2 Habilitar ngrok (túnel)

Meta **no** puede ver la red local de la VM, por lo que se crea un túnel HTTPS con ngrok.

En la VM:

```
ngrok http 5000
```

Esto expone el Flask local (`http://localhost:5000`) como una URL pública HTTPS.

### 2.3 Registrar el webhook en Meta

En la sección WhatsApp → Configuración:

* Establecer la URL pública generada por ngrok
* Añadir el token de verificación elegido
* Habilitar los campos:

  * `messages`
  * `message_template_status_update`

Meta valida el webhook usando la petición de prueba con `hub.challenge`, la cual el servidor Flask debe responder correctamente.

---

# 3. Flujo Webhook → ROS 2

### Lo que ocurre cuando el usuario envía un mensaje por WhatsApp:

1. Usuario escribe:
   `forward 50`
   o cualquier comando válido.

2. Meta recibe el mensaje en la nube.

3. Meta reenvía inmediatamente el mensaje al **Webhook Flask** en la VM a través del túnel ngrok.

4. El servidor Flask:

   * Lee el contenido del mensaje
   * Lo guarda en la cola FIFO interna
   * Deja disponible el mensaje más reciente en `GET /next`

---

# 4. Ejecución del Nodo de WhatsApp en Docker

El nodo ROS 2 que procesa mensajes de WhatsApp **no corre en la VM directamente**, sino dentro de un **contenedor Docker que también está dentro de la VM**.


### 4.1 Ejecutar el contenedor

Con red compartida para acceder al Flask en la VM:

```
docker run --network=host tello_whatsapp_img
```

Esto garantiza que el contenedor puede consultar:

```
http://localhost:5000/next
```

El contenedor “ve” el localhost de la VM, no el del host físico.

### 4.2 Función del nodo ROS 2 dentro del contenedor

El nodo:

1. Lee del archivo de configuración la dirección y puerto del webhook
   (en este caso siempre: `localhost:5000`)
2. Construye la URL:
   `http://localhost:5000/next`
3. Ejecuta un temporizador que consulta periódicamente al servidor
4. Si hay un comando nuevo, lo añade a la `mission_queue`
5. Cuando no hay más comandos y ya se recibió al menos uno:
   `mission_loaded = True`
6. Espera confirmación del failsafe (batería segura)
7. Inicia la misión y publica comandos en `/tello/command`

---

# 5. Integración con el Nodo DroneConnectorNode

El nodo DroneConnectorNode corre en la VM y:

* Está suscrito a `/tello/command`
* Recibe los comandos publicados por el nodo WhatsApp en Docker
* Ejecuta las acciones reales usando la librería `djitellopy`

Ejemplo:

1. Usuario envía al WhatsApp:
   `takeoff`
2. Nodo WhatsApp obtiene el comando en `/next`
3. Nodo WhatsApp publica en ROS:
   `/tello/command = "takeoff"`
4. DroneConnectorNode recibe el comando
5. DroneConnectorNode ejecuta:
   `tello.takeoff()`
6. El dron despega

---

# 6. Resumen Completo del Flujo Total

### **Secuencia general:**

1. **Usuario** envía mensaje por WhatsApp.
2. **Meta** recibe y reenvía al webhook.
3. **ngrok** dirige el mensaje a la VM.
4. **Servidor Flask** recibe el mensaje → lo guarda en la cola → lo expone en `/next`.
5. **Docker (nodo ROS 2)** consulta periódicamente `/next`.
6. Nodo procesa el comando → lo añade a misión → lo envía como `/tello/command`.
7. **MissionPlannerNode** ejecuta la misión paso a paso (timers, delays, waits).
8. **DroneConnectorNode** toma `/tello/command` y controla el dron vía WiFi.
9. **Dron Tello** ejecuta el movimiento físico.
10. Telemetría y vídeo fluyen desde el dron → ROS → nodos de análisis y seguridad.
