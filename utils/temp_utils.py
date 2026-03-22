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

def check_state(temp: float) -> float:
    """Comprueba la temperatura actual para asignarle un ratio de aumento"""
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


def check_phase(i: int) -> str:
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

# ===================
# FUNCIONES DE ESTADO
# ===================

def temp_increase(phase: str, ratio: float, temperature: float) -> float:
    """
    Añade ruido a la señal simulada

    El incremento depende del ratio, la varianza y la phase

    Parámetros
    ─────────────────────────────
    phase: str
        Fase del ascenso del cohete, con posibles valores:
        - reposo (0): primeros 5 segundos (aumento de temperatura explosivo).
        - ignición (1): entre 5 y 10 segundos, combustión del material, explosión de temperatura
        - ascenso (2): entre 10 y 25 segundos (aumento de temperatura moderado).
        - estable (3): a partir de 15 segundos (aumento de temperatura bajo / nulo).
        Cada fase tendrá una desviación típica asociada al nivel de interferencias que se produzcan
    
    ratio: float
        Factor de ajuste que simula la respuesta del sistema ante sobrecalentamiento.
        Multiplica a la desviación típica (reduciéndola) cuando se superan ciertos umbrales de seguridad.

    temperature: float
        Temperatura actual del sistema.

    Returns
    ─────────────────────────────
    noisy_temp: float
        Nueva temperatura tras al aplicar el incremento
    """
    


    # Ruido variante segun la fase de la misión
    std_d = 0
    if phase == 0:
        std_d = 0.5
    elif phase == 1:
        std_d = 15 # Fase con mayores turbulencias
    elif phase == 2:
        std_d = 5
    elif phase == 3:
        std_d = 3
    else:
        return -1

    noisy_temp = add_gaussian_noise(mean=0.0, std_d=std_d, measure=temperature)
    return noisy_temp

def apply_inverse_cooling_law(temperature: float, ext_temperature: float, k: float=0.8, t: int=0) -> float:
    """
    Utiliza la ley de enfriamiento de Newton con el exponencial inverso para aproximar el aumento de temperatura que se
    produce durante la ignición del cohete (más realista que un aumento lineal).
    """
    T_heat = round(temperature + (ext_temperature - temperature) * (1 - exp(-k  * (t - 5))),  4)
    return T_heat

def apply_cooling_law(temperature: float, ext_temperature=10.0, k: float=0.02, t: int=1) -> float:
    """
    Utiliza la ley de enfriamiento de Newton de forma iterativa para calcular la temperatura en cada instante de tiempo
    desde el fin de la combustión.
    """
    T_cool= round(temperature + (ext_temperature - temperature) * exp(-k  * (t - 10)),  4)
    return T_cool

def compute_ext_temperature(h: float):
    """Aproxima la temperatura ambiente dada la altura en km."""
    h = h / 1000.0
    return 15 - 6.5 * h