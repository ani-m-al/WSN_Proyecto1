#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from djitellopy import Tello
import cv_bridge
import cv2

from sensor_msgs.msg import Image
from std_msgs.msg import Int32, String

class TelloNode(Node):
    def __init__(self):
        super().__init__('tello_node')
        self.get_logger().info('Nodo Tello iniciado.')

        # Conexión con el dron
        self.drone = Tello()
        try:
            self.drone.connect()
        except Exception as e:
            self.get_logger().error(f'Error al conectar con Tello: {e}')
            rclpy.shutdown()
            return

        # Iniciar video
        self.drone.streamon()
        self.reader = self.drone.get_frame_read()
        self.bridge = cv_bridge.CvBridge()

        # Publicadores
        self.pub_img = self.create_publisher(Image, '/tello/image_raw', 10)
        self.pub_batt = self.create_publisher(Int32, '/tello/battery', 10)
        self.pub_velx = self.create_publisher(Int32, '/tello/speed_x', 10)
        self.pub_alt = self.create_publisher(Int32, '/tello/height', 10)

        # Suscriptor de comandos
        self.sub_cmd = self.create_subscription(String, '/tello/command', self.cmd_callback, 10)

        # Temporizadores
        self.timer_vid = self.create_timer(1.0 / 60.0, self.video_cb)
        self.timer_tel = self.create_timer(2.0, self.telemetry_cb)

    # --- Comandos ---
    def cmd_callback(self, msg):
        cmd = msg.data.strip().lower()
        try:
            if cmd == "takeoff":
                self.drone.takeoff()
            elif cmd == "land":
                self.drone.land()
            elif cmd == "emergency":
                self.drone.emergency()
            elif len(cmd.split()) == 2:
                c, v = cmd.split()
                v = int(v)
                if c == "forward":
                    self.drone.move_forward(v)
                elif c == "back":
                    self.drone.move_back(v)
                elif c == "up":
                    self.drone.move_up(v)
                elif c == "down":
                    self.drone.move_down(v)
                elif c == "left":
                    self.drone.move_left(v)
                elif c == "right":
                    self.drone.move_right(v)
                elif c == "cw":
                    self.drone.rotate_clockwise(v)
                elif c == "ccw":
                    self.drone.rotate_counter_clockwise(v)
        except Exception as e:
            self.get_logger().warn(f'Error comando: {e}')

    # --- Video ---
    def video_cb(self):
        try:
            frame = self.reader.frame
            if frame is not None:
                msg = self.bridge.cv2_to_imgmsg(frame, 'bgr8')
                msg.header.stamp = self.get_clock().now().to_msg()
                self.pub_img.publish(msg)
        except Exception:
            pass

    # --- Telemetría ---
    def telemetry_cb(self):
        try:
            b = self.drone.get_battery()
            msg_b = Int32()
            msg_b.data = b
            self.pub_batt.publish(msg_b)

            vx = self.drone.get_speed_x()
            msg_vx = Int32()
            msg_vx.data = vx
            self.pub_velx.publish(msg_vx)

            h = self.drone.get_height()
            msg_h = Int32()
            msg_h.data = h
            self.pub_alt.publish(msg_h)
        except Exception as e:
            self.get_logger().warn(f'Error al obtener telemetría: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = TelloNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
    	pass
    finally:
        if hasattr(node, 'drone'):
            try:
                if node.drone.is_flying:
                    node.drone.land()
                node.drone.streamoff()
            except Exception:
                pass
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

