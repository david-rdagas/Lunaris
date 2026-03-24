"""
========================================
SIMULADOR DE BARÓMETRO

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

20-03-2026
========================================
"""

from numpy import linspace
from utils.noise import add_gaussian_noise
from utils.sensor2client import prepare_publisher
import json
from time import sleep
from datetime import datetime, timezone, timedelta



# Valores realistas de presión
"""
HACER TRANSFORMADOR DE ALTURA A PRESIÓN PARA QUE SEA MÁS FÁCIL MODIFICARLO
"""
PRESSURE_AT_500 = 954.61 #hPa
PRESSURE_AT_1500 = 845.56

# Valores estadísticos del error normal del sensor
MEAN = 0
STANDARD_D = 0.4

def baro_start_measure(client, frequency: int, i:int , duration: int, rest_end: int, launch_end: int, apogee_end: int, descent_end: int):
    """
    Función que recrea las medidas de presión que un barómetro real recogería durante un vuelo real, las fases que atraviesa son:
    
        - Reposo: 5s
        - Ascenso: 20s
        - Apogeo: 1s
        - Descenso 79s
    """
    # ── 2. Simulación de presión y publicación de datos  ──────────────────────────────────────────

    pressure_on_launch = linspace(PRESSURE_AT_500, PRESSURE_AT_1500, launch_end - rest_end) # Duración del "launch"
    pressure_on_descent = linspace(PRESSURE_AT_1500, PRESSURE_AT_500, descent_end - apogee_end) # Duración del descenso
    

    if i <= rest_end:
        baro_measurement = add_gaussian_noise(MEAN, STANDARD_D, PRESSURE_AT_500)
        print(baro_measurement)

    elif rest_end < i <= launch_end:
        launch_second = i - rest_end - 1
        baro_measurement = add_gaussian_noise(MEAN, STANDARD_D, pressure_on_launch[launch_second])

    elif launch_end < i <= apogee_end:
        baro_measurement = add_gaussian_noise(MEAN, STANDARD_D, PRESSURE_AT_1500)

    elif apogee_end < i <= descent_end:
        descent_second = i - apogee_end - 1
        baro_measurement = add_gaussian_noise(MEAN, STANDARD_D, pressure_on_descent[descent_second])

        descent_second = i - apogee_end - 1
        baro_measurement = add_gaussian_noise(MEAN, STANDARD_D, pressure_on_descent[descent_second])

    else:
        print("Simulation fatal error")

    baro_measurement = round(baro_measurement, 4)
    
    if i % frequency == 0:    
        payload = json.dumps({
            "device_id": "s-barometer-01",
            "measure_id": str(i),
            "timestamp": datetime.now(timezone(timedelta(hours=1))).isoformat(),
            "type": "pressure",
            "unit": "hPa",
            "value": baro_measurement
        })

        client.publish(
            "rocket/general/s-barometer-01/data",
            payload,
            qos=0 #Provisional
        )




# Conversión altitud → presión (dejarla estar de momento aunque no se use para procesado)
def pressure_to_altitude(pressure: float, p0: float = 1013.25) -> float:
    return (288.15 / 0.0065) * (1 - (pressure / p0) ** 0.190263)