FROM osrf/ros:jazzy-desktop

LABEL maintainer="am@ucuenca.edu.ec"

# Instalación de herramientas básicas y dependencias de ROS
RUN apt update && apt upgrade -y && \
    apt install -y \
    python3-colcon-common-extensions \
    nano \
    python3-pip \
    tree \
    net-tools \
    python3-opencv \
    python3-requests \
    ros-${ROS_DISTRO}-vision-opencv \
    netcat-openbsd \
    influxdb-client \
    python3-numpy && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Librerías adicionales
RUN pip3 install av pillow djitellopy --no-deps --break-system-packages
RUN pip3 install influxdb-client --break-system-packages

# Workspace ROS2
RUN mkdir -p /root/ros2_ws/src
WORKDIR /root/ros2_ws/src

# Crear paquete
RUN /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
    ros2 pkg create --build-type ament_python drone_controller --license MIT"

# Copiar código del paquete
WORKDIR /root/ros2_ws/src/drone_controller
COPY config/setup.py .
WORKDIR /root/ros2_ws/src/drone_controller/drone_controller
COPY nodes/*.py .

# Compilar
WORKDIR /root/ros2_ws
RUN /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && colcon build"

# Cargar entorno ROS2
RUN echo "source /root/ros2_ws/install/setup.bash" >> ~/.bashrc

# Shell por defecto
CMD ["bash"]

