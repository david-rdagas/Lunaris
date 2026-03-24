import paho.mqtt.client as mqtt
def prepare_publisher(id: str, status_topic: str):
#Función auxiliar lo suficiente abstraida como para usarse con los 3 sensores

    #Crear cliente
    client = mqtt.Client(client_id=id)

    #Establecer LWT
    client.will_set(
        status_topic,
        "OFFLINE",
        qos=0,
        retain=True
    )
    
    
    #Conectar al broker y marcar como online
    client.connect("localhost", 1883, 60)

    client.publish(
        status_topic,
        "ONLINE",
        qos=0,
        retain=True
    )

    return client