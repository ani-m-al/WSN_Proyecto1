#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String, Bool

class BatterySafeNode(Node):
    """Nodo de seguridad: aterrizaje automático si la batería es baja."""
    
    LIMIT = 40  # Umbral de batería (%)

    def __init__(self):
        super().__init__('battery_safe_node')
        self.get_logger().info(f'Nodo de seguridad iniciado (umbral {self.LIMIT}%)')

        self.triggered = False  # Evita múltiples comandos "land"

        # Suscriptor al nivel de batería
        self.batt_sub = self.create_subscription(Int32, '/tello/battery', self.check_battery, 10)

        # Publicadores
        self.cmd_pub = self.create_publisher(String, '/tello/command', 10)
        self.safe_pub = self.create_publisher(Bool, '/tello/safety_status', 10)

    def check_battery(self, msg):
        """Verifica el nivel de batería y activa el aterrizaje si es necesario."""
        level = msg.data
        safe = level >= self.LIMIT

        # Publicar estado de seguridad
        self.safe_pub.publish(Bool(data=safe))

        if safe:
            if self.triggered:
                self.get_logger().info(f'Batería OK ({level}%). Failsafe desactivado.')
            self.triggered = False
        else:
            if not self.triggered:
                self.get_logger().warn(f'Batería baja: {level}%. Enviando comando LAND.')
                self.cmd_pub.publish(String(data="land"))
                self.triggered = True
            else:
                self.get_logger().info(f'Failsafe activo. Esperando aterrizaje... ({level}%)')

def main(args=None):
    rclpy.init(args=args)
    node = BatterySafeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Nodo de seguridad finalizado.')
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

