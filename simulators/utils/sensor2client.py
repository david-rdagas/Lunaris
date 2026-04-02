"""
========================================
GESTIÓN MQTT

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

22-03-2026
========================================
"""

import paho.mqtt.client as mqtt

def prepare_publisher(id: str, status_topic: str):
    """
    Función de inicialización de publisher lo suficiente abstraida como para usarse con los 3 sensores
    """
    client = mqtt.Client(client_id=id)

    #Establecer LWT
    client.will_set(status_topic, "OFFLINE", qos=1, retain=True)
    
    #Conectar al broker y marcar como online
    client.connect("mosquitto", 1883, 60)
    client.loop_start()
    client.publish(status_topic, "ONLINE", qos=1, retain=True)
    return client