# Módulo de sensorica

Los datos de la misión han sido simulados con valores cercanos a la realidad. Cada archivo contiene su propia implementación con las simplificaciones necesarias para una generación eficiente de datos artificiales.

---

## Sensores disponibles

### 1. Barometro

Simula la variación de presión atmosférica que registraría un barómetro real durante las fases del vuelo. Los parámetros de la misión son configurables:

- **Duración de cada fase** → [`main.py`](../main.py)
- **Altitud inicial y máxima** → [`s_barometer.py`](./s_barometer.py)

![Simulacion de presion](../docs/pressure_sim.png)

> **Simplificación:** dentro de cada fase (ascenso y descenso) se asume velocidad vertical constante, distribuyendo el gradiente de presión en intervalos discretos de un segundo.