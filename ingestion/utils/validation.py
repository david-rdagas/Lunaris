import json

def valid_data_message(payload_str: str) -> bool:
    """Devuelve True si el mensaje recibido es válido, False si no."""
    
    # 1. JSON válido
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError:
        return False
    
    # 2. Campos obligatorios presentes
    required = ["device_id", "measure_id", "type", "timestamp", "unit"]
    for field in required:
        if field not in data:
            return False
    
    # 3. value es numérico
    return True


def valid_status_message(payload_str: str) -> bool:
    return payload_str.lower() in ["online", "offline"]