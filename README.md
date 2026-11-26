# SCHOS — Sistema de Organización de Horarios Académicos

Proyecto académico de Programación Orientada a Objetos.

## Ejecutar

Se requiere Python 3.10 o superior. Desde la raíz del repositorio:

```console
py main.py
```

## Guardar y cargar datos

Al iniciar, SCHOS carga `datos/schos.json` si existe. La opción **6. Guardar** almacena el estado actual. Si ya existía un archivo, se conserva una copia de respaldo `.bak`.

Si el JSON no se puede leer o no tiene un formato compatible, el programa muestra un error y no reemplaza los datos con un sistema vacío.

El archivo JSON y sus respaldos son datos locales y están excluidos de Git.

## Estructura

- `modelos/`: usuarios, aulas, recursos académicos, horarios y matrículas.
- `servicios/`: registro de aulas, planificación y consultas.
- `persistencia.py`: guardado y recuperación del sistema en JSON.
- `aplicacion.py`: registros y contadores de identificadores.
- `main.py`: menú de consola.
- `pruebas/`: pruebas automatizadas.

## Estado actual

Las opciones de recursos académicos, espacios, consulta de registros y guardado están disponibles en el menú. Las opciones generales de planificación y matrícula siguen pendientes de integración.

## Ejecutar las pruebas

```console
py -m unittest discover -s pruebas -v
```

Cada integrante trabaja en una rama para su tarea y abre un pull request para revisar los cambios antes de incorporarlos a `main`.
