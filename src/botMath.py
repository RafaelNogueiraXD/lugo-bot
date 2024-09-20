from abc import ABC
import lugo4py
import  math

def get_distance( obstacle_x, obstacle_y, x1, y1, x2, y2):
    A = obstacle_x - x1
    B = obstacle_y - y1
    C = x2 - x1
    D = y2 - y1

    dot = A * C + B * D
    len_sq = C * C + D * D
    param = -1 if len_sq == 0 else dot / len_sq

    if param < 0:
        xx, yy = x1, y1
    elif param > 1:
        xx, yy = x2, y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D

    dx = obstacle_x - xx
    dy = obstacle_y - yy
    distance = {
        'dist': (dx**2 + dy**2) ** 0.5,
        'between': param >= 0 and param <= 1

    }
    return distance


def calculate_new_position( origin_position, distance, angle_degrees):


    angle_radians = math.radians(angle_degrees)

    delta_x = distance * math.cos(angle_radians)
    delta_y = distance * math.sin(angle_radians)
    new_position = {
        "x" : origin_position.x + delta_x,
        "y" : origin_position.y + delta_y
    }

    return new_position

def calculate_rebound(point_init : lugo4py.Point, point_final : lugo4py.Point):
    x_inicial = point_init.x
    y_inicial = point_init.y
    x_final = point_final.x
    y_final = point_final.y
    
    y_refletido = -y_final
    

    if y_refletido - y_inicial != 0:
        m = (x_final - x_inicial) / (y_refletido - y_inicial)
    else:
        m = float('inf') 
    
    b = x_inicial - m * y_inicial
    
    x_colisao = m * 0 + b 
    
    return lugo4py.Point(x_colisao , 0)
