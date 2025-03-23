#!/usr/bin/env python3
# Shebang 

import rospy  
import math  
from geometry_msgs.msg import Twist 
from turtlesim.msg import Pose  
from std_srvs.srv import Empty  # resetear la simulación.

class TurtleControl:
    def __init__(self):
        rospy.init_node('turtle_keyboard_control', anonymous=True)  # Inicializa un nodo ROS.
        self.pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)  # Publicador para enviar comandos de velocidad.
        self.pose_sub = rospy.Subscriber('/turtle1/pose', Pose, self.update_pose)  # Suscriptor para obtener la posición actual.
        self.current_pose = None  # Inicializa la pose actual de la tortuga.
        self.rate = rospy.Rate(10)  # Establece la tasa de ciclos del bucle en 10 Hz.
        self.turtle_size = 0.5  # Asume un tamaño de la tortuga para cálculos de colisión.

    def update_pose(self, data):
        self.current_pose = data  # Actualiza la posición actual con los datos recibidos.

    def move_to_point(self, target_x, target_y, kp_linear=1.0, kp_angular=2.0):
        while not rospy.is_shutdown():
            if self.current_pose is None:
                continue  # Espera hasta que la posición actual esté disponible.

            # Calcula el ángulo hacia el objetivo y la distancia.
            angle_to_target = math.atan2(target_y - self.current_pose.y, target_x - self.current_pose.x)
            distance = math.sqrt((target_x - self.current_pose.x) ** 2 + (target_y - self.current_pose.y) ** 2)

            # Ajusta la orientación para enfrentar al objetivo.
            angle_error = angle_to_target - self.current_pose.theta
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

            # Control proporcional para girar hacia el objetivo o avanzar hacia él.
            if abs(angle_error) > 0.01: #error umbral
                twist = Twist()
                twist.angular.z = kp_angular * angle_error
                self.pub.publish(twist)
            elif distance > 0.05: #error umbral
                twist = Twist()
                twist.linear.x = kp_linear * distance
                twist.angular.z = kp_angular * angle_error
                self.pub.publish(twist)
            else:
                print(f"Reached corner at ({self.current_pose.x:.2f}, {self.current_pose.y:.2f})")
                break

            self.rate.sleep()

        self.pub.publish(Twist())  # Detiene la tortuga después de alcanzar el punto porque si no se des estabiliza.
        rospy.sleep(0.5)

    def valid_position(self, x, y):
        # Verifica que la posición esté dentro de un rango permitido.
        return x >= self.turtle_size and x <= 11 - self.turtle_size and y >= self.turtle_size and y <= 11 - self.turtle_size

    def request_position(self):
        while True:
            try:
                x, y = map(float, input("Ingrese las coordenadas de inicio para dibujar la figura (x, y): ").split())
                if self.valid_position(x, y):
                    return x, y
                else:
                    print("La posición es inválida, la figura estaría fuera del área de dibujo. Intente nuevamente.")
            except ValueError:
                print("Entrada inválida. Por favor, ingrese coordenadas numéricas.")

    def draw_figure(self, figure_type):
        start_x, start_y = self.request_position()
        self.move_to_point(start_x, start_y)  # Mueve la tortuga a la posición inicial.

        # Dibuja un rombo o un pentágono según el tipo de figura elegido.
        if figure_type == 'rhombus':
            # Código para dibujar un rombo.
        elif figure_type == 'pentagon':
            # Código para dibujar un pentágono.

    def run(self):
        while not rospy.is_shutdown():
            print("Press 'r' to draw rhombus, 'p' to draw pentagon, 'x' to exit")
            command = input().strip().lower()
            if command == 'x':
                break
            elif command == 'r':
                self.draw_figure('rhombus')
            elif command == 'p':
                self.draw_figure('pentagon')

if __name__ == '__main__':
    try:
        turtle_control = TurtleControl()
        turtle_control.run()  # Ejecuta el control principal del programa.
    except rospy.ROSInterruptException:
        pass  # Maneja la excepción de interrupción de ROS.
