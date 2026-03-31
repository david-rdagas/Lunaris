import paho.mqtt.client as mqtt
import json
from utils.sliding_window import window_update, window_alarm

# ── 1. Callback: conexión ──────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code:", rc)

    client.subscribe("rocket/+/+/data", qos=1)

    client.subscribe ("rocket/+/+/status", qos=1)
    

# ── 2. Callback: mensaje recibido ──────────────────────────────────────────
sliding_window_termometer = []
sliding_window_barometer = []
def on_message(client, userdata, msg):
    payload = msg.payload.decode()


    print("\nTopic:", msg.topic)
    
    if msg.topic.endswith("/data"):
        try:
            #1. Crear ventana deslizante y ajustarla a la temperatura 
            data = json.loads(payload)
            print("Data:", data)
            
        except json.JSONDecodeError:
            print("JSON Error:", payload)

        if msg.topic.endswith("/s-termometer-01/data"):
            window_update(data['value'], sliding_window_termometer, 5)
            window_alarm(sliding_window_termometer, alarm_threshold=810.0, data='temperatura')
            
        if msg.topic.endswith("/s-barometer-01/data"):
            window_update(data['value'], sliding_window_barometer, 10)
            window_alarm(sliding_window_barometer, alarm_threshold=800.0, data='presion')
            

    else:
        print("Status message:", payload)
    
        

# ── 3. Callback: desconexión ──────────────────────────────────────────
def on_disconnect(client, userdata, rc):
    print("Disconnected from broker", rc)

# ── 4. Creación de cliente ──────────────────────────────────────────
client = mqtt.Client(client_id="subscriber-01")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# ── 5. Conexión de cliente y bucle ──────────────────────────────────────────

client.connect("localhost", 1883, 60)
client.loop_forever()