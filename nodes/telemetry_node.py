#!/usr/bin/env python3

import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuración de InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "mi-token-secreto"
INFLUX_ORG = "ParrotOrg"
INFLUX_BUCKET = "tello_data"

class TelemetryNode(Node):
    def __init__(self):
        super().__init__('telemetry_node')
        self.get_logger().info('📡 Nodo de telemetría iniciado.')

        # Variables locales
        self.battery = -1
        self.speed_x = 0
        self.height = 0

        # Conexión con InfluxDB
        self.db_client = None
        self.db_writer = None
        try:
            self.db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
            self.db_writer = self.db_client.write_api(write_options=SYNCHRONOUS)
            self.get_logger().info(f'Conectado a InfluxDB en {INFLUX_URL}')
        except Exception as e:
            self.get_logger().error(f'No se pudo conectar a InfluxDB: {e}')

        # Suscriptores
        self.sub_battery = self.create_subscription(Int32, '/tello/battery',
            lambda msg: self.handle_data(msg, "battery", "%"), 10)
        self.sub_speed = self.create_subscription(Int32, '/tello/speed_x',
            lambda msg: self.handle_data(msg, "speed_x", "cm/s"), 10)
        self.sub_height = self.create_subscription(Int32, '/tello/height',
            lambda msg: self.handle_data(msg, "height", "cm"), 10)

        # Temporizador para mostrar los datos
        self.timer = self.create_timer(0.5, self.show_data)

    def handle_data(self, msg, field, units):
        """Procesa los datos recibidos y los guarda en InfluxDB."""
        value = msg.data

        # Guardar valor local
        if field == "battery":
            self.battery = value
        elif field == "speed_x":
            self.speed_x = value
        elif field == "height":
            self.height = value

        # Guardar en InfluxDB
        if self.db_writer:
            try:
                point = (
                    Point("tello_data")
                    .tag("field", field)
                    .tag("units", units)
                    .field("value", value)
                    .time(None, WritePrecision.MS)
                )
                self.db_writer.write(bucket=INFLUX_BUCKET, record=point)
            except Exception as e:
                self.get_logger().debug(f'Error al guardar {field}: {e}')

    def show_data(self):
        """Muestra los últimos valores en pantalla."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.get_logger().info('--- TELEMETRÍA DEL DRON ---')
        self.get_logger().info(f'Batería: {self.battery} %')
        self.get_logger().info(f'Altura: {self.height} cm')
        self.get_logger().info(f'Velocidad X: {self.speed_x} cm/s')
        if not self.db_writer:
            self.get_logger().warn('⚠️ InfluxDB no disponible. Modo local.')
        self.get_logger().info('(Ctrl+C para salir)')

    def destroy_node(self):
        """Cierra la conexión al detener el nodo."""
        if self.db_client:
            self.db_client.close()
            self.get_logger().info('Conexión con InfluxDB cerrada.')
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = TelemetryNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if node:
            node.get_logger().error(f'Error: {e}')
    finally:
        if node:
            node.destroy_node()
        print("\nNodo de telemetría finalizado.")
        rclpy.shutdown()

if __name__ == '__main__':
    main()

