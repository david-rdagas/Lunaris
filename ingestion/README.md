# Módulo de ingesta

Los datos simulados por los sensores pasan al módulo de ingesta mediante un broker Mosquitto, para pasar por los siguientes procesos: 

---

## Extracción de características
Se procesa el mensaje recibido en una función feature_extraction, que devuelve
- raw_message: Mensaje decodificado completo
- sensor_id: Id del sensor
- msg_type: Tipo de mensaje (distinguiendo mensajes tipo data y tipo status)

## Validación
Se comprueba si los mensajes tienen un formato válido antes de continuar

## Aplicación de sliding windows
Se crean diversas sliding windows temporales para comprobar que los valores que se reciben de los sensores no sean atípicos, dando alarmas en caso contrario.

## Guardado en TSBD
Se envían los datos del mensaje a InfluxDB

