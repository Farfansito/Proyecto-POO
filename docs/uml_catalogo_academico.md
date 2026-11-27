# UML del catálogo académico

Este diagrama describe los modelos académicos mantenidos por Kevin y el
contrato de demanda que puede consultar el planificador.

```mermaid
classDiagram
    class Asignatura {
        +String codigo
        +String nombre
        +int creditos
        +int horas_teoricas
        +int horas_practicas
        +demanda_semanal
        +horas_requeridas(tipo_sesion)
        +actualizar_datos(...)
    }

    class Nivel {
        +int numero
        +String nombre
        +agregar_asignatura(asignatura)
        +buscar_asignatura(codigo)
        +obtener_asignaturas()
    }

    class Paralelo {
        +String codigo
        +String jornada
        +int cupo_maximo
        +Nivel nivel
        +PeriodoAcademico periodo
        +agregar_asignacion(asignacion)
    }

    class PeriodoAcademico {
        +String codigo
        +String estado
        +paralelos
        +abrir_periodo()
        +agregar_paralelo(paralelo)
    }

    Nivel "1" o-- "0..*" Asignatura : catálogo
    Nivel "1" <-- "0..*" Paralelo : nivel
    PeriodoAcademico "1" o-- "0..*" Paralelo : periodo
```

`Asignatura.demanda_semanal` devuelve horas semanales separadas por tipo de
sesión. La duración y cantidad de bloques se determinan en planificación
cuando el equipo acuerde la duración de bloque.

El código de paralelo se normaliza y se mantiene único dentro del periodo,
porque la persistencia JSON actual reconstruye paralelos usando ese código.
