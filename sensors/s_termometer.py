"""
========================================
SIMULADOR DE TERMÓMETRO

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

21-03-2026
========================================
"""

from utils.temp_utils import *
from time import sleep


def temp_start_measure(duration: int, rest_end: int, launch_end: int, apogee_end: int, descent_end: int):
    temperatures = []
    temperature = 20.0
    for i in range(0, duration - 1):
        # Comprobación del estado
        ratio = check_state(temperature)
        phase = check_phase(i)
        if i <= rest_end:
            temperature = 20.0
            print(temperature)
            temperatures.append(temperature)

        elif rest_end < i <= launch_end:
            temperature = temp_increase(phase, ratio, temperature)
            print(temperature)
            temperatures.append(temperature)

        elif launch_end < i <= apogee_end:
            external_temperature = 10.0
            temperature = apply_cooling_law(temperature, external_temperature)
            print(temperature)
            temperatures.append(temperature)

        elif apogee_end < i <= descent_end:
            h = 1500.0
            external_temperature = compute_ext_temperature(h)
            temperature = apply_cooling_law(temperature, external_temperature)
            print(temperature)
            temperatures.append(temperature)
            h -= 1500.0 / float(descent_end - apogee_end) #Simplificación, descenso uniforme

        else:
            print("Simulation fatal error")
        sleep(1)