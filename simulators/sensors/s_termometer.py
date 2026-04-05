"""
========================================
SIMULADOR DE TERMÓMETRO

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

21-03-2026
========================================
"""

from numpy import linspace, random
from utils.temp_utils import *
import json
from datetime import datetime, timezone, timedelta

# Variables ajustables al vuelo
TEMPERATURE_AT_REST = 20 #Celsius
MAX_TEMPERATURE = 800
MEAN = 0
STANDARD_D = 0.8
STD_D_IGNITION = 15
STD_D_LAUNCH = 5
STD_D_DESCENT = 3


def temp_start_measure(client, frequency: int, i: int, duration: int, rest_end: int, launch_end: int, apogee_end: int, descent_end: int):
    """
    Función que simula la temperatura de la carcasa del motor en cada fase del vuelo de forma realista.
    """
    termo_measurement = -1 # Valor de error
    ignition_end = 10

    # Comprobación del estado
    phase = check_phase(i)

    # ── 1. Generación de temperatura ─────────────────────────────────────────────────────────────
    if i <= rest_end:
        temperature = TEMPERATURE_AT_REST
        termo_measurement = add_gaussian_noise(MEAN, STANDARD_D, temperature)

    elif rest_end < i <= ignition_end:
        h = 700
        external_temperature = compute_ext_temperature(h)
        termo_measurement = apply_inverse_cooling_law(temperature=TEMPERATURE_AT_REST , t=i)

    elif ignition_end < i <= launch_end:
        h_launch_array = linspace(700, 1500, 15)
        h = h_launch_array[i - 10 - 1]
        external_temperature = compute_ext_temperature(h)
        termo_measurement = apply_cooling_law(temperature=TEMPERATURE_AT_REST, t=i)

    elif launch_end < i <= apogee_end:
        h = 1500
        external_temperature = compute_ext_temperature(h)
        termo_measurement = apply_cooling_law(temperature=TEMPERATURE_AT_REST, t=i)

    elif apogee_end < i <= descent_end:
        h_launch_array = linspace(1500, 700, 79)
        h = h = h_launch_array[i - 26 - 1]
        external_temperature = compute_ext_temperature(h)
        termo_measurement = apply_cooling_law(temperature=TEMPERATURE_AT_REST, t=i)

    else:
        print("Simulation fatal error")


    # ── 2. Envío MQTT ─────────────────────────────────────────────────────────────
    if random.randint(0,100) > 99:
        termo_measurement += random.uniform(-termo_measurement/100.0, termo_measurement/100.0)
    
    print(f"[TERMÓMETRO] Enviado paquete con valor: {termo_measurement} ºC")
    if i % frequency == 0:
        payload = json.dumps({
            "device_id": "s-termometer-01",
            "measure_id": str(i),
            "timestamp": datetime.now(timezone(timedelta(hours=1))).isoformat(),
            "type": "temperature",
            "unit": "ºC",
            "value": termo_measurement
        })

        client.publish(
            "rocket/control/s-termometer-01/data",
            payload,
            qos=0 #Provisional
        )