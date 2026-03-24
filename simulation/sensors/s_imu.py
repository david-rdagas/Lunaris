"""
========================================
SIMULADOR DE IMU

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

22-03-2026
========================================
"""

import numpy as np
from math import exp
from utils.noise import add_gaussian_noise
import json
from datetime import datetime, timezone, timedelta

# ── 1. Parámetros de misión globales ─────────────
_duration    = -1
_rest_end    = -1
_launch_end  = -1
_apogee_end  = -1
_descent_end = -1


# ── 2. Constantes de ruido (ejes estables x e y) ────────────────────────────────────────────────────
ACCEL_NOISE_COMBUSTION = 2.0
ACCEL_NOISE_REST       = 0.15
GYRO_NOISE_COMBUSTION  = 3.0
GYRO_NOISE_REST      = 0.5



# ── 3. Punto de entrada principal ───────────────────────────────────────────
def imu_start_measure(client, frequency: int , i: int, duration: int, rest_end: int, launch_end: int, apogee_end: int, descent_end: int) -> None:
    """Punto de entrada al sensor. Inicializa parámetros de misión y lanza cada componente."""
    

    global _duration, _rest_end, _launch_end, _apogee_end, _descent_end
    _duration    = duration
    _rest_end    = rest_end
    _launch_end  = launch_end
    _apogee_end  = apogee_end
    _descent_end = descent_end

    acc = accelerometer_start_measure(i)
    gyro = gyroscope_start_measure(i)

    if i % frequency == 0:
        payload = json.dumps({
            "device_id": "s-imu-01",
            "measure_id": str(i),
            "timestamp": datetime.now(timezone(timedelta(hours=1))).isoformat(),
            "type": "direction",
            "unit": "m/s**2 & rad/s",
            "acceleration_data": acc,
            "gyroscope_data": gyro
        })

        client.publish(
            "rocket/orientation/s-imu-01/data",
            payload,
            qos=0 #Provisional
        )



# ── 4. Acelerómetro ───────────────────────────────────────────────────────────
def accelerometer_start_measure(i: int):
    accel_packet = []
    accel_packet.append(measure_x_axis_a(i))
    accel_packet.append(measure_y_axis_a(i))
    accel_packet.append(measure_z_axis_a(i))
    print(accel_packet)
    
    return accel_packet


def measure_x_axis_a(t: int) -> float:
    std = ACCEL_NOISE_COMBUSTION if _rest_end <= t < _launch_end else ACCEL_NOISE_REST
    return add_gaussian_noise(mean=0, std_d=std, measure=0)


def measure_y_axis_a(t: int) -> float:
    std = ACCEL_NOISE_COMBUSTION if _rest_end <= t < _launch_end else ACCEL_NOISE_REST
    return add_gaussian_noise(mean=0, std_d=std, measure=0)


def measure_z_axis_a(t: int) -> float:
    if t < _rest_end:
        return add_gaussian_noise(mean=9.8, std_d=0.05, measure=9.8)
    elif t < _launch_end:
        elapsed = t - _rest_end
        thrust = 9.8 + 35 * (1 - exp(-0.8 * elapsed))
        return add_gaussian_noise(mean=0, std_d=ACCEL_NOISE_COMBUSTION, measure=thrust)
    elif t < _apogee_end:
        elapsed = t - _launch_end
        coast = 9.8 + 35 * exp(-0.3 * elapsed)
        return add_gaussian_noise(mean=0, std_d=ACCEL_NOISE_REST, measure=coast)
    elif t < _apogee_end + 1:
        return add_gaussian_noise(mean=0, std_d=ACCEL_NOISE_REST, measure=0)
    else:
        return add_gaussian_noise(mean=0, std_d=ACCEL_NOISE_REST, measure=-4.0)



# ── 5. Giroscopio ─────────────────────────────────────────────────────────────
def gyroscope_start_measure( i: int):
    gyro_packet = []
    gyro_packet.append(measure_x_axis_g(i))
    gyro_packet.append(measure_y_axis_g(i))
    gyro_packet.append(measure_z_axis_g(i))
    
    return gyro_packet


def measure_x_axis_g(t: int) -> float:
    std = GYRO_NOISE_COMBUSTION if _rest_end <= t < _launch_end else GYRO_NOISE_REST
    return add_gaussian_noise(mean=0, std_d=std, measure=0)


def measure_y_axis_g(t: int) -> float:
    std = GYRO_NOISE_COMBUSTION if _rest_end <= t < _launch_end else GYRO_NOISE_REST
    return add_gaussian_noise(mean=0, std_d=std, measure=0)


def measure_z_axis_g(t: int) -> float:
    std = GYRO_NOISE_COMBUSTION / 2 if _rest_end <= t < _launch_end else GYRO_NOISE_REST / 2
    return add_gaussian_noise(mean=0, std_d=std, measure=0)