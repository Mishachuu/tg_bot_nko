def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Вычисляет расстояние между двумя точками в километрах (Haversine формула).
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Радиус Земли в км
    
    # Преобразуем градусы в радианы
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Разница координат
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Формула Haversine
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    
    print(f"      📐 РАСЧЕТ РАССТОЯНИЯ:")
    print(f"         Точка 1: ({lat1}, {lon1})")
    print(f"         Точка 2: ({lat2}, {lon2})")
    print(f"         Результат: {distance:.6f} км")
    
    return distance