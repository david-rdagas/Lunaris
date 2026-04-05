<h1><p align="center">Lunaris</p></h1>

<p align="center">
  <img src="docs/images/lunaris_logo.png" width="250" align="center"/>
</p>

<p align="center">
  Sistema IoT de control de constantes principales para cohetería
</p>

---

Proyecto con fines teóricos en el que se implementa la cadena completa del ciclo de datos en un sistema IoT simulando una misión de cohetería. Lunaris es el nombre que recibe un cohete amateur cuya misión es alcanzar los 1.000 metros de altura y descender con éxito para su reutilización en posteriores misiones, la finalidad de la expedición es la obtención de datos que los sensores abajo detallados recogerán y serán de utilidad para simulaciones, ajustes y mejoras en futuros proyectos de la compañía. 

## Sobre nuestra propuesta
A continuación se expone la visión general del sistema, cada componente de los que se habla dispone de su propio README.md en donde se trata a profundidad su implementación.

### Qué se incluye en él?

Tratamos de implementar una aproximación de lo que sería cada una de las fases del procesado de datos en tiempo real.

<p align="center">
  <img src="docs/images/iot_cycle.png" alt="Ciclo de datos IoT" width="600"/>
</p>


<p align="center">
  <em>Ciclo de datos IoT: sensores → protocolos → ingesta/almacenamiento → API/dashboards</em>
</p>

1. **Sensores y "things"**: en la primera fase, los sensores capturan datos de la realidad. Una cosa es cualquier elemento del mundo real que emita datos que podamos capturar, en nuestro caso, trabajaremos con el cohete y los datos que genera al llevar a cabo la misión.

2. **Comunicaciones**: la comunicación (a nivel de aplicación) se lleva a cabo mediante MQTT, un protocolo de mensajería que funciona con un broker MQTT como intermediario para implementar el patrón publisher/subscriber. Cada componente de la sensórica publica en tópicos personalizados, esto podría haber sido implementado con un único publisher centralizado que publicara datos de todos los sensores diferenciandolos en el contenido de sus cambios, posiblemente una aproximación más realista (sistema de sensores controlados por una ESP32).

3. **Ingesta y almacenamiento**: a su vez, el servicio de ingesta se suscribe a todos estos tópicos para obtener información tanto de estado como de los valores obtenidos, realizando un filtro, comprobando rangos de valores y almacenando los resultados en una base de datos en tiempo real (TSDB), en nuestra implementación, InfluxDB.

4. **Visualización y servicios**: 


### Como se estructura el proyecto?

```
lunaris/
├── docs/
│── sensors/               # Simuladores de datos
│     ├── barometer.py
│     ├── README.md
│     ├── sensor2.py
│     └── sensor3.py
│── utils/
│     ├── noise.py
│     └── README.md
├── .env
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```

## Despliegue del sistema
Descarga nuestro repositorio y ejecútalo por tu cuenta:
``` bash
git clone git@github.com:david-rdagas/Lunaris.git
```
El proyecto se agrupa en un conjunto de contenedores, por tanto no es necesario la instalación de paquetería adicional más allá de Docker, para crear e inicializar el sistema basta con:

``` bash
docker compose up
```
Sobre la raíz del proyecto.

Cabe destacar que el repositorio de github viene sin las claves del .env, necesarias para el funcionamiento íntegro del proyecto. 