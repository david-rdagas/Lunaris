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


