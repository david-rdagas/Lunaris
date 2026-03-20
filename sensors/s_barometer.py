"""
========================================
SIMULADOR DE BARÓMETRO

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

20-03-2026
========================================
"""

from utils.noise import add_gaussian_noise


# Valores realistas de presión
PRESSURE_AT_500 = 954.61 #hPa
PRESSURE_AT_1500 = 845.56

# Valores estadísticos del error normal del sensor
MEAN = 0
STANDARD_D = 0.4

def baro_start_measure(duration: int, rest_end: int, launch_end: int, apogee_end: int, descent_end: int):
    """
    Función que recrea las medidas de presión que un barómetro real recogería durante un vuelo real, las fases que atraviesa son:
    
        - Reposo: 5s
        - Ascenso: 20s
        - Apogeo: 1s
        - Descenso 79s
    """
    
    for i in range(0, duration + 1):
        if i <= rest_end:
            baro_measurement = add_gaussian_noise(MEAN, STANDARD_D, PRESSURE_AT_500)
            print(baro_measurement)
        elif rest_end < i <= rest_end:
            pass
        elif rest_end < i <= launch_end:
            pass
        elif launch_end < i <= apogee_end:
            pass
        elif apogee_end < i <= descent_end:
            pass
        else:
            print("Simulation fatal error")




# Conversión altitud → presión (dejarla estar de momento aunque no se use para procesado)
def pressure_to_altitude(pressure: float, p0: float = 1013.25) -> float:
    return (288.15 / 0.0065) * (1 - (pressure / p0) ** 0.190263)