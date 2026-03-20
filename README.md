# **Lunaris: Simulador de Control en Cohetería**

Proyecto con fines teóricos en el que se implementa la cadena completa del ciclo de datos en un sistema IoT simulando una misión de cohetería. Lunaris es el nombre que recibe un cohete amateur cuya misión es alcanzar los 1.000 metros de altura y descender con éxito para su reutilización en posteriores misiones, la finalidad de la expedición es la obtención de datos que los sensores abajo detallados recogerán y serán de utilidad para simulaciones, ajustes y mejoras en futuros proyectos de la compañía. 

## Sobre nuestra propuesta

### Qué se incluye en él?

Tratamos de implementar una aproximación de lo que sería cada una de las fases del procesado de datos en tiempo real.

<p align="center">
  <img src="docs/iot_cycle.png" alt="Ciclo de datos IoT" width="600"/>
</p>


<p align="center">
  <em>Ciclo de datos IoT: sensores → protocolos → ingesta/almacenamiento → API/dashboards</em>
</p>

1. **Things**:
2. **Comunicaciones**:
3. **Ingesta y almacenamiento**:
4. **Visualización y servicios**: 


### Como se estructura el proyecto?

```
lunaris/
├── docs/
│   └── sensors/
│       ├── barometer.py
│       ├── README.md
│       ├── sensor2.py
│       └── sensor3.py
│   └── utils/
│       ├── noise.py
│       └── README.md
├── .env
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```