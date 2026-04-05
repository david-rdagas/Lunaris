"""
========================================
SERVICIO DE INGESTA

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

26-03-2026
========================================
"""

import json
import os
from datetime import datetime, timezone
import time
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

from utils.sliding_window import update_window, window_alarm
from utils.validation import valid_data_message, valid_status_message


# ── 1. Conexión con TSDB (InfluxDB) ──────────────────────────────────────────
load_dotenv()
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

def connect_influx():
    while True:
        try:
            client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
            health = client.health()
            if health.status == "pass":
                print("Conectado a InfluxDB!")
                return client
        except Exception as e:
            print(f"Esperando a InfluxDB... {e}")
            time.sleep(2)

def write_to_influx(point):
    try:
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        print(f"[OK] Dato escrito correctamente")
    except Exception as e:
        print(f"[ERROR] Fallo al escribir en InfluxDB: {e}")


influx_client = connect_influx()
write_api = influx_client.write_api(write_options=SYNCHRONOUS)


# ── 2. Comunicación de estado del subscriber MQTT ──────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    print("Servicio de ingesta conectado como subscriber!")
    client.subscribe("rocket/+/+/data", qos=1)
    client.subscribe("rocket/+/+/status", qos=1)

def on_disconnect(client, userdata, rc):
    print("El servicio de ingesta se ha desconectado del broker", rc)


# ── 3. Procesado de datos entrantes ──────────────────────────────────────────
windows = {}

def feature_extraction(msg):
    raw_message = msg.payload.decode()
    topic_split = msg.topic.split('/')
    sensor_id = topic_split[2]
    msg_type  = topic_split[3]
    return raw_message, sensor_id, msg_type


def on_message(client, userdata, msg):
    """
    Cada vez que la ingesta (única) recibe un dato (3 posibles fuentes + 3 status), se llevan a cabo los siguientes pasos:
        - 1. Extracción de características.
        - 2. Diferenciamos entre datos con 'value' y datos de 'status':
        - 3. Validación
        - 4. Diferenciamos entre datos de imu y otros (diferente formato json) (solo con datos de 'value')
        - 5. Actualización de sliding window (solo con datos de 'value')
        - 6. Guardado en TSDB
    """
    # 1.
    raw_message, sensor_id, msg_type = feature_extraction(msg)
    print(f"[INGESTA] Se ha recibido el paquete: {raw_message}")

    # 2.
    if msg_type == "data":
        # 3.
        if not valid_data_message(raw_message):
            return # No se procesa el mensaje
        data_dict = json.loads(raw_message)

        # 4.
        if data_dict["device_id"] == "s-imu-01":
            point_acc = (
                Point('s-imu-01/acc')
                .tag("type", data_dict["type"])
                .tag("unit", "m/s**2")
                .field("acc_x", float(data_dict["acceleration_data"][0]))
                .field("acc_y", float(data_dict["acceleration_data"][1]))
                .field("acc_z", float(data_dict["acceleration_data"][2]))
                .time(datetime.fromisoformat(data_dict["timestamp"]))
            )

            point_gyro = (
                Point('s-imu-01/gyro')
                .tag("type", data_dict["type"])
                .tag("unit", "rad/s")
                .field("gyro_x", float(data_dict["gyroscope_data"][0]))
                .field("gyro_y", float(data_dict["gyroscope_data"][1]))
                .field("gyro_z", float(data_dict["gyroscope_data"][2]))
                .time(datetime.fromisoformat(data_dict["timestamp"]))
            )
            write_to_influx(point_acc)
            write_to_influx(point_gyro)

        else: # Termómetro o barómetro
            # 5.
            mean = update_window(windows=windows, device_id=data_dict['device_id'], timestamp_str=data_dict['timestamp'], value=data_dict['value'])
            window_alarm(mean, data_dict['device_id'])

            point = (
                Point(data_dict['device_id'])
                .tag("type", data_dict["type"])
                .tag("unit", data_dict["unit"])
                .field("value", float(data_dict["value"]))
                .time(datetime.fromisoformat(data_dict["timestamp"]))
            )
            write_to_influx(point)

    elif msg_type == "status":
        # 3.
        if not valid_status_message(raw_message):
            return

        measurement = sensor_id
        point = (
                Point(measurement)
                .field("status", raw_message)
                .time(datetime.now(timezone.utc))
        )
        write_to_influx(point)


# ── 4. Creación de cliente ──────────────────────────────────────────
client = mqtt.Client(client_id="subscriber-01")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect("mosquitto", 1883, 60)
client.loop_forever()