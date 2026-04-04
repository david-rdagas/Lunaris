"""
========================================
GESTIÓN MQTT

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

22-03-2026
========================================
"""

import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Se ha conectado {userdata['nombre']} como publisher!")
        client.publish(userdata["topico"], "online", qos=1, retain=True)
    else:
        print(f"Ha ocurrido un error con la conexión al Brocker!!: rc = {rc}")


def on_disconnect(client, userdata, rc):
    print(f"Se ha desconectado {userdata['nombre']} (publisher)")


def prepare_publisher(id: str, status_topic: str):
    """
    Función de inicialización de publisher lo suficiente abstraida como para usarse con los 3 sensores
    """
    client = mqtt.Client(client_id=id, clean_session=True)

    #Establecer LWT
    client.will_set(status_topic, "offline", qos=0, retain=True)
    client.user_data_set({"nombre": id, "topico": status_topic})
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    #Conectar al broker y marcar como online
    client.max_inflight_messages_set(100)
    client.connect("mosquitto", 1883, 60)
    client.loop_start()
    time.sleep(2) 
    return client