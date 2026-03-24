"""
========================================
RECURSOS PARA SENSOR DE TEMPERATURA

Autores: David Rodríguez Dagas
         Adrián Pérez Domínguez

20-03-2026
========================================
"""

from utils.noise import add_gaussian_noise
from math import exp

# ===================
# FUNCIONES DE ESTADO
# ===================
def check_phase(i: int) -> int:
    """Comprueba el segundo de operación para determinar la fase
    Codificación: 
        - Reposo: 0
        - Ignición: 1
        - Ascenso: 2
        - Estable (descenso): 3

    
    """
    phase = -1 #Valor de error
    if i < 5:
        phase = 0
    elif 5 <= i < 10:
        phase = 1
    elif 10 <= i < 25:
        phase = 2
    else:
        phase = 3
    
    return phase

# ====================
# FUNCIONES DE CÁLCULO
# ====================
def apply_inverse_cooling_law(temperature: float, max_temperature: float = 800.0, k: float=0.8, t: int=0) -> float:
    """
    Utiliza la ley de enfriamiento de Newton con el exponencial inverso para aproximar el aumento de temperatura que se
    produce durante la ignición del cohete (más realista que un aumento lineal).
    """
    T_heat = round(temperature + (max_temperature - temperature) * (1 - exp(-k  * (t - 5))),  4)
    return T_heat


def apply_cooling_law(temperature: float, max_temperature=800.0, k: float=0.02, t: int=1) -> float:
    """
    Utiliza la ley de enfriamiento de Newton de forma iterativa para calcular la temperatura en cada instante de tiempo
    desde el fin de la combustión.
    """
    T_cool= round(temperature + (max_temperature - temperature) * exp(-k  * (t - 10)),  4)
    return T_cool


def compute_ext_temperature(h: float) -> float:
    """Aproxima la temperatura ambiente dada la altura en km."""
    h = h / 1000.0
    return 15 - 6.5 * h