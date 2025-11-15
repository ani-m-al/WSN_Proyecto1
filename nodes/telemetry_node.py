#!/usr/bin/env python3

import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class TelemetryNode(Node):
    """
    Nodo de telemetría:
    - Se suscribe a /tello/battery
    - Se suscribe a /tello/speed_x
    - Se suscribe a /tello/height
    - Muestra todos los datos en la terminal de forma continua
    """

    def __init__(self):
        super().__init__('telemetry_node')
        self.get_logger().info('Nodo de telemetría iniciado.')

        # Variables locales
        self.battery = -1
        self.speed_x = 0
        self.height = 0

        # Suscriptores
        self.sub_battery = self.create_subscription(
            Int32, '/tello/battery',
            lambda msg: self.handle_data(msg, "battery"), 10
        )
        self.sub_speed = self.create_subscription(
            Int32, '/tello/speed_x',
            lambda msg: self.handle_data(msg, "speed_x"), 10
        )
        self.sub_height = self.create_subscription(
            Int32, '/tello/height',
            lambda msg: self.handle_data(msg, "height"), 10
        )

        # Temporizador del dashboard
        self.timer = self.create_timer(0.5, self.show_data)

    def handle_data(self, msg, field):
        """Procesa los datos de telemetría."""
        value = msg.data

        if field == "battery":
            self.battery = value
        elif field == "speed_x":
            self.speed_x = value
        elif field == "height":
            self.height = value

    def show_data(self):
        """Muestra los últimos valores en pantalla."""
        os.system('cls' if os.name == 'nt' else 'clear')

        self.get_logger().info('--- TELEMETRÍA DEL DRON ---')
        self.get_logger().info(f'Batería: {self.battery} %')
        self.get_logger().info(f'Altura: {self.height} cm')
        self.get_logger().info(f'Velocidad X: {self.speed_x} cm/s')
        self.get_logger().info('(Ctrl+C para salir)')

    def destroy_node(self):
        """Cierra correctamente el nodo."""
        self.get_logger().info('Cerrando nodo de telemetría.')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = TelemetryNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node:
            node.destroy_node()
        print("\nNodo de telemetría finalizado.")
        rclpy.shutdown()


if __name__ == '__main__':
    main()
