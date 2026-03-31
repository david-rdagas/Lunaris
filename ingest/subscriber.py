import paho.mqtt.client as mqtt
import json
from utils.sliding_window import window_update, window_alarm
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os 
from dotenv import load_dotenv

load_dotenv()


INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")


influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

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


    topic_split = msg.topic.split('/')
    if len(topic_split) < 4:
        return

    sector = topic_split[1]
    sensor_id = topic_split[2]
    msg_type = topic_split[3]

    print(f"\n[TOPIC] {msg.topic}")

    # Prepara el objeto point, necesario para InfluxDB
    point = Point("rocket_metrics") \
        .tag("system", sector) \
        .tag("sensor", sensor_id)

    

    if msg_type == "data":
        data = json.loads(payload)

        if 'value' in data:
            valor = float(data['value'])
            point.field("value", valor)
            
            # Tu lógica de alarmas (solo si hay 'value')
            if sensor_id == "s-termometer-01":
                window_update(valor, sliding_window_termometer, 5)
                window_alarm(sliding_window_termometer, 810.0, 'temperatura')
            elif sensor_id == "s-barometer-01":
                window_update(valor, sliding_window_barometer, 10)
                window_alarm(sliding_window_barometer, 800.0, 'presion')

        elif "acceleration_data" in data and "gyroscope_data" in data:
                acc = data["acceleration_data"]
                gyro = data["gyroscope_data"]
                
                # Aplanamos los datos para InfluxDB
                point.field("acc_x", float(acc[0]))
                point.field("acc_y", float(acc[1]))
                point.field("acc_z", float(acc[2]))
                point.field("gyro_x", float(gyro[0]))
                point.field("gyro_y", float(gyro[1]))
                point.field("gyro_z", float(gyro[2]))
                
                # Tags adicionales que vienen en tu JSON
                point.tag("measure_type", data.get("type", "direction"))
                point.tag("unit", data.get("unit", "m/s2_rad/s"))

        # Escribir en InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print("Envio exitoso a InfluxDB!")
    

    elif msg_type == "status":
        point.field("status_msg", payload)
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
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