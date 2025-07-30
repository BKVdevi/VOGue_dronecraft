#!/usr/bin/env python3

import rospy
import math
from clover import srv
from std_srvs.srv import Trigger

# --- НАСТРОЙКИ ---

# Замените на 1, 2, 3, 4 – выбор "роли" дрона
DRONE_NUMBER = 1

# Позиции в кубе относительно центра ArUco-24
cube_positions = {
    1: (-1, -1),  # левый нижний угол куба
    2: (1, -1),   # правый нижний угол куба  
    3: (-1, 1),   # левый верхний угол куба
    4: (1, 1),    # правый верхний угол куба
}

# --- ИНИЦИАЛИЗАЦИЯ ---

rospy.init_node('flight')

get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
land = rospy.ServiceProxy('land', Trigger)
set_effect = rospy.ServiceProxy('led/set_effect', srv.SetLEDEffect)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def navigate_wait(x=0, y=0, z=0, yaw=float('nan'), speed=0.5, frame_id='', auto_arm=False, tolerance=0.2):
    """Лететь в точку и ждать прилета"""
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id, auto_arm=auto_arm)
    
    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id='navigate_target')
        if math.sqrt(telem.x ** 2 + telem.y ** 2 + telem.z ** 2) < tolerance:
            break
        rospy.sleep(0.2)

def land_wait():
    """Посадка и ожидание приземления"""
    land()
    while get_telemetry().armed:
        rospy.sleep(0.2)

# --- ОСНОВНОЙ АЛГОРИТМ ---

def main():
    # 1. Взлет с синей индикацией
    set_effect(r=0, g=0, b=255)  # Синий цвет
    navigate_wait(x=0, y=0, z=1.5, speed=0.5, frame_id='map', auto_arm=True)
    rospy.sleep(1)
    
    # 2. Полет к позиции в кубе над ArUco-24
    cube_x, cube_y = cube_positions[DRONE_NUMBER]
    set_effect(r=255, g=255, b=255)  # Белый цвет для построения
    #navigate_wait(x=3, y=3, z=1.5, speed=0.5)
    navigate_wait(x=3.5 + cube_x, y=3.5 + cube_y, z=1.5, speed=0.5, frame_id='map')
    
    # 3. Удержание позиции минимум 3 секунды
    rospy.loginfo("Holding cube position for 3 seconds...")
    rospy.sleep(8)
    
    # 4. Возврат к стартовой позиции с радужной индикацией
    set_effect(effect='rainbow')  # Радужный эффект
    navigate_wait(x=0, y=0, z=1.5, speed=0.5, frame_id='map', auto_arm=True)
    rospy.sleep(1)
    
    # 5. Посадка
    land_wait()
    rospy.loginfo("Mission completed successfully!")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass