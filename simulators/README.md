# Módulo de sensórica

Los datos de la misión han sido simulados con valores cercanos a la realidad. Cada archivo contiene su propia implementación con las simplificaciones necesarias para una generación eficiente de datos artificiales.

---

## Sensores disponibles

### 1. Barometro

Simula la variación de presión atmosférica que registraría un barómetro real durante las fases del vuelo. Los parámetros de la misión son configurables:

- **Duración de cada fase** → [`main.py`](../main.py)
- **Altitud inicial y máxima** → [`s_barometer.py`](./s_barometer.py)

![Simulacion de presion](../docs/pressure_sim.png)

> **Simplificación:** dentro de cada fase (ascenso y descenso) se asume velocidad vertical constante, distribuyendo el gradiente de presión en intervalos discretos de un segundo.

### 2. Termómetro

Simula la variación en la temperatura interior del cohete, colocada en una zona cercana al motor. La simulación recoge cambios de temperatura acordes a las diferentes fases de la misión. Los parámetros de la misión son configurables:

- **Duración de cada fase** → [`main.py`](../main.py)
- **Temperatura inicial y máxima, desviaciones de temperatura en cada fase** → [`s_termometer.py`](./s_termometer.py)

> **Simplificación:** Se aplica en hasta el final de la fase de ignición la inversa de la ley de enfriamiento de Newton, con el objetivo de mostrar un comportamiento verosímil en cuanto a los aumentos de temperatura. Sin embargo, la inversa de esta ley no es fiel a la naturaleza, solo es una herramienta para simular el comportamiento deseado de la temperatura.

### 3. IMU

Sensor que hace de giroscopio y acelerómetro, por lo que simula la orientación (en 3 ejes) como la velocidad (en 3 ejes). Los parámetros de la misión son configurables

- **Duración de cada fase** → [`main.py`](../main.py)


