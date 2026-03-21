"""
========================================
GENERADOR DE RUÍDO

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

20-03-2026
========================================
"""

import numpy as np

def add_gaussian_noise(mean: float, std_d: float, measure: float) -> float:
    "Añade ruido a una señal simulada con una distribución Gaussiana"
    noise = np.random.normal(mean, std_d)
    return measure + noise


def check_state(temp: float):
    "Comprueba la temperatura actual para asignarle un ratio de aumento"
    ratio = 1.0
    if temp > 700.00:
        ratio = 0.9
    if temp > 750.00:
        ratio = 0.8
    if temp > 800.00:
        ratio = 0.5
    else:
        ratio = 1.0
    return ratio

def check_phase(i: int):
    "Comprueba el segundo de operación para determinar la fase"
    phase = "None"
    if i < 5:
        phase = "encendido"
    elif 5 <= i < 15: 
        phase = "ascenso"
    else:
        phase = "estable"
    
    return phase

def temp_increase(phase: str, ratio: float, temperature: float):
    '''
    Calcula un incremento aleatorio de temperatura y lo aplica a la temperatura actual.

    El incremento depende del ratio y, la varianza y la phase

    Parámetros
    ─────────────────────────────
    phase: str
        Fase del ascenso del cohete, con posibles valores:
        - "encendido": primeros 5 segundos (aumento de temperatura explosivo).
        - "ascenso": entre 5 y 15 segundos (aumento de temperatura moderado).
        - "estable": a partir de 15 segundos (aumento de temperatura bajo / nulo).
        Cada fase tendrá una desviación típica asociada.
    
    ratio: float
        Factor de ajuste que simula la respuesta del sistema ante sobrecalentamiento.
        Multiplica a la desviación típica (reduciéndola) cuando se superan ciertos umbrales de seguridad.

    temperature: float
        Temperatura actual del sistema.

    Returns
    ─────────────────────────────
    new_temp: float
        Nueva temperatura tras al aplicar el incremento
    '''

    std_d = 0
    if phase == "encendido":
        std_d = 120.0
    elif phase == "ascenso":
        std_d = 30.0
    elif phase == "estable":
        std_d = 5.0

    extra = np.abs(np.random.normal(0.0, std_d))
    new_temp = temperature + extra
    return new_temp

def apply_cooling_law(temperature: float, temp_amb=10.0, k=0.02, dt= 1):
    "Utiliza la ley de enfriamiento de Newton de forma iterativa para restarle temperatura respecto a la ambiental"
    return temperature - k * (temperature - temp_amb) * dt + np.random.uniform(-0.5, 0.5)

def compute_temp_amb(h: float):
    "Aproxima la temperatura ambiente dada la altura en km."
    h = h / 1000.0
    return 15 - 6.5 * h


