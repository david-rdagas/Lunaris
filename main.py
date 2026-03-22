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

def simulation() -> None:

    DURATION = DESCENT_END = 105
    REST_END = 5
    LAUNCH_END = 25
    APOGEE_END = 26

    baro_start_measure(DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)
    # imu_start_measure(DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)
    temp_start_measure(DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)



def tests():
    DURATION = DESCENT_END = 105
    REST_END = 5
    LAUNCH_END = 25
    APOGEE_END = 26
    baro_start_measure(DURATION, REST_END, LAUNCH_END, APOGEE_END, DESCENT_END)


if __name__ == "__main__":
    #simulation()
    tests()