#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Int32

import requests
import time
import os


# === CONFIG HOST ===
HOST_ADDR = os.environ.get("HOST_ADDR", "127.0.0.1")
HOST_PORT = int(os.environ.get("HOST_PORT", "5000"))
API_TOKEN = os.environ.get("API_TOKEN", "nodetoken123")
FETCH_INTERVAL = float(os.environ.get("FETCH_INTERVAL", "0.5"))

FETCH_URL = f"http://{HOST_ADDR}:{HOST_PORT}/next"
FETCH_HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}


class MissionPlannerNode(Node):
    """
    MISSION PLANNER con:
        - seguridad por battery (failsafe)
        - seguridad por conexión (connector_node)
        - misión dinámica desde WhatsApp (webhook)
    """

    def __init__(self):
        super().__init__('mission_planner')

        self.get_logger().info("Mission Planner iniciado (WhatsApp-driven)")

        # --- Estados ---
        self.mission_started = False
        self.is_safe_to_fly = False
        self.is_connected = False
        self.current_height = 0
        self.mission_step = 0

        # La misión se cargará dinámicamente desde WhatsApp
        self.mission_queue = []
        self.mission_loaded = False

        # Timers
        self.mission_timer = None
        self.height_check_timer = None

        # --- ROS interfaces ---
        self.command_pub = self.create_publisher(String, '/tello/command', 10)

        self.safety_sub = self.create_subscription(
            Bool, '/tello/safety_status', self.safety_callback, 10
        )

        self.height_sub = self.create_subscription(
            Int32, '/tello/height', self.height_callback, 10
        )

        self.connection_sub = self.create_subscription(
            Bool, '/tello/connection_status', self.connection_callback, 10
        )

        # Timer del poll al webhook
        self.create_timer(FETCH_INTERVAL, self.fetch_mission_msgs)

        self.get_logger().info("Esperando batería OK + conexión + misión para iniciar...")

    # ----------------------------------------------------------------------
    # SUBS
    # ----------------------------------------------------------------------
    def safety_callback(self, msg):
        self.is_safe_to_fly = msg.data

        if not self.is_safe_to_fly:
            self.get_logger().warn("Advertencia: batería baja o failsafe activo.")
            return

        # Si ya tenemos misión cargada y dron conectado → arrancar misión
        if self.is_safe_to_fly and not self.mission_started and self.mission_loaded and self.is_connected:
            self.get_logger().info("Seguridad OK + conexión OK + misión cargada. Iniciando en 3s...")
            self.mission_started = True
            self.create_timer(3.0, self.start_mission)

    def height_callback(self, msg):
        self.current_height = msg.data

    def connection_callback(self, msg):
        self.is_connected = msg.data

        if not self.is_connected:
            self.get_logger().warn("Dron desconectado. Misión en pausa.")
            return

        # Si conectó y tenemos misión + batería OK → podemos iniciar
        if self.is_connected and self.is_safe_to_fly and self.mission_loaded and not self.mission_started:
            self.get_logger().info("Dron conectado + misión lista + batería OK → iniciando en 3s")
            self.mission_started = True
            self.create_timer(3.0, self.start_mission)

    # ----------------------------------------------------------------------
    # FETCH MISSION (WhatsApp → Host → Nodo)
    # ----------------------------------------------------------------------
    def fetch_mission_msgs(self):
        """Obtiene comandos 1 por 1 desde el host y construye mission_queue."""
        if self.mission_started:
            return  # ya estamos ejecutando misión, no pedimos más comandos

        try:
            resp = requests.get(FETCH_URL, headers=FETCH_HEADERS, timeout=2)
        except Exception as e:
            self.get_logger().warn(f"No se pudo consultar host: {e}")
            return

        if resp.status_code != 200:
            return

        j = resp.json()

        if j.get("status") == "ok":
            cmd = j["text"].strip()
            self.mission_queue.append(cmd)
            self.get_logger().info(f"[WhatsApp] Añadido: {cmd}")
        elif j.get("status") == "empty":
            # Si ya tenemos al menos 1 comando → misión completa
            if len(self.mission_queue) > 0 and not self.mission_loaded:
                self.mission_loaded = True
                self.get_logger().info(f"MISIÓN cargada desde WhatsApp: {self.mission_queue}")

    # ----------------------------------------------------------------------
    # MISSION EXECUTION
    # ----------------------------------------------------------------------
    def start_mission(self):
        self.get_logger().info("Comenzando misión...")
        self.execute_next_step()

    def execute_next_step(self):
        if self.mission_step >= len(self.mission_queue):
            self.get_logger().info("MISIÓN COMPLETADA.")
            self.mission_started = False
            self.mission_loaded = False
            return

        command = self.mission_queue[self.mission_step]
        self.get_logger().info(f"Paso {self.mission_step+1}/{len(self.mission_queue)} → {command}")

        self.mission_step += 1  # advance pointer early

        # Delay
        if command.startswith("delay_"):
            delay_time = float(command.split("_")[1])
            self.get_logger().info(f"PAUSA de {delay_time} segundos")
            self.mission_timer = self.create_timer(delay_time, self.execute_next_step)
            return

        # Wait height
        if command == "wait_height":
            self.get_logger().info("Esperando altura >= 50 cm")
            self.height_check_timer = self.create_timer(1.0, self.wait_for_height_callback)
            return

        # Command normal
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)

        self.get_logger().info(f"Comando enviado a /tello/command: {command}")
        # No llamamos execute_next_step() aquí → lo hará el siguiente delay o wait
        return

    def wait_for_height_callback(self):
        TARGET = 50
        if self.current_height >= TARGET:
            self.get_logger().info(f"Altura objetivo alcanzada ({self.current_height} cm)")
            self.height_check_timer.cancel()
            self.execute_next_step()
        else:
            self.get_logger().info(f"Esperando altura... {self.current_height}/{TARGET} cm")


def main(args=None):
    rclpy.init(args=args)
    node = MissionPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.get_logger().info("Cerrando Mission Planner")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
