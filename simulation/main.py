"""
========================================
ENTRADA DEL SIMULADOR

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

20-03-2026
========================================
"""

from sensors.s_barometer import baro_start_measure
from sensors.s_imu import imu_start_measure
from sensors.s_termometer import temp_start_measure
from utils.sensor2client import prepare_publisher
from time import sleep

def simulation() -> None:

    DURATION = DESCENT_END = 105
    REST_END = 5
    LAUNCH_END = 25
    APOGEE_END = 26

    # ── 1. Crear los 3 clientes ──────────────────────────────────────────
    client_temp = prepare_publisher("s-termometer-01", "rocket/system/s-termometer-01/status")
    client_baro = prepare_publisher("s-barometer-01", "rocket/system/s-termometer-01/status")
    client_imu = prepare_publisher("s-imu-01", "rocket/system/s-imu-01/status")

    for i in range (0, DURATION + 1):
        baro_start_measure(client_baro, 1, i, DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)
        temp_start_measure(client_temp, 1, i, DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)
        imu_start_measure(client_imu, 1, i, DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)
        sleep(1)


if __name__ == "__main__":
    simulation()
