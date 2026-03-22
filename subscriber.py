import paho.mqtt.client as mqtt
import json

# ── 1. Callback: conexión ──────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code:", rc)

    client.subscribe("rocket/+/+/data", qos=1)

    client.subscribe ("rocket/+/+/status", qos=1)

# ── 2. Callback: mensaje recibido ──────────────────────────────────────────


def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    print("\nTopic:", msg.topic)
    
    if msg.topic.endswith("/data"):
        try:
            data = json.loads(payload)
            print("Data:", data)
            
        except json.JSONDecodeError:
            print("JSON Error:", payload)

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