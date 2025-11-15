#!/usr/bin/env python3
import os
# Mantener compatibilidad Docker/X11 si corresponde
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2


class VideoViewerNode(Node):
    """
    Suscribe a /tello/image_raw, convierte a OpenCV y muestra el video en pantalla.
    Asume que el nodo emisor ya dibujó rectángulos/texto sobre el frame publicado.
    """
    def __init__(self):
        super().__init__('video_viewer')
        self.get_logger().info('Iniciando el nodo Visualizador de Video.')
        self.get_logger().info('Esperando fotogramas en el tópico /tello/image_raw...')

        # CV Bridge
        self.bridge = CvBridge()

        # Suscripción al tópico
        self.subscription = self.create_subscription(
            Image,
            '/tello/image_raw',
            self.image_callback,
            10
        )

        # Crear la ventana una sola vez (WINDOW_NORMAL evita comportamientos extra)
        window_name = 'Tello Video'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # Opcional: ajustar tamaño inicial (puedes cambiar si quieres)
        cv2.resizeWindow(window_name, 960, 720)
        self.window_name = window_name

    def image_callback(self, msg):
        """
        Convierte el mensaje ROS (rgb8) a BGR y muestra la ventana.
        Si el emisor ya dibujó rectángulos y texto, aquí se verá tal cual.
        """
        try:
            # Recibe 'rgb8' según tu nodo emisor; convertimos a numpy RGB
            frame_rgb = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

            # Convertir RGB -> BGR para OpenCV
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # Mostrar en ventana (sin barras extra; ventana normal)
            cv2.imshow(self.window_name, frame_bgr)
            # waitKey es necesario para que la ventana se refresque
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Si presionan 'q' en la ventana, cerramos el nodo
                self.get_logger().info("Cierre solicitado por tecla 'q' en la ventana.")
                # Llamamos a destruir nodo de forma segura
                self.destroy_node()
                rclpy.shutdown()

        except CvBridgeError as e:
            self.get_logger().error(f'Error de CV-Bridge: {e}')
        except Exception as e:
            self.get_logger().error(f'Error al procesar el fotograma: {e}')

    def destroy_node(self):
        """Limpia recursos al cerrar el nodo."""
        self.get_logger().info('Cerrando el nodo Visualizador de Video y ventanas.')
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    video_node = VideoViewerNode()
    try:
        rclpy.spin(video_node)
    except KeyboardInterrupt:
        video_node.get_logger().info('KeyboardInterrupt recibido, cerrando.')
    finally:
        try:
            video_node.destroy_node()
        except Exception:
            pass
        rclpy.shutdown()


if __name__ == '__main__':
    main()

