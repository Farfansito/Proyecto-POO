# Aporte de Kevin: integración y revisión académica

## Escenario de demostración

Se registra el periodo académico `2027A` (del 1 de enero al 30 de junio de 2027),
el nivel `1 - Primero` y la asignatura `POO - Programación` (3 créditos,
2 horas teóricas y 2 prácticas). La asignatura se incorpora al catálogo del
nivel. Después se abre el periodo y se crea el paralelo `A`, jornada matutina,
con cupo para 30 estudiantes y referencias al mismo nivel y periodo registrados.
Finalmente, el paralelo se agrega al periodo abierto.

La prueba `test_escenario_integrado_conserva_referencias_del_catalogo`, en
`pruebas/test_kevin.py`, comprueba con identidad de objeto (`assertIs`) que el
sistema, el nivel, la asignatura, el paralelo y el periodo conservan las mismas
instancias durante ese flujo.

## Contratos comprobados

- `SistemaSCHOS.establecer_periodo`, `registrar_nivel` y
  `registrar_asignatura` registran las instancias recibidas bajo sus claves.
- `Nivel.agregar_asignatura` exige un objeto `Asignatura` y rechaza códigos
  duplicados.
- `Paralelo` exige objetos `Nivel` y `PeriodoAcademico`, y conserva ambas
  referencias.
- `PeriodoAcademico.agregar_paralelo` exige que el periodo esté abierto, que el
  paralelo apunte a esa misma instancia de periodo y que su código no esté
  repetido. La propiedad `paralelos` entrega una copia de la lista, sin clonar
  sus objetos.

## Contrato de demanda para planificación

`Asignatura.demanda_semanal` expone las horas semanales requeridas en un
diccionario nuevo con las claves `TEORIA` y `PRACTICA`. Por ejemplo, una
asignatura con dos horas teóricas y dos prácticas entrega
`{"TEORIA": 2, "PRACTICA": 2}`. `Asignatura.horas_requeridas(tipo_sesion)` permite
consultar un tipo de forma individual y normaliza mayúsculas y espacios. Un
tipo distinto de `TEORIA` o `PRACTICA` se rechaza.

La demanda representa horas semanales; no fija cuántos bloques debe generar el
motor. La conversión a bloques depende de la duración acordada por el equipo y
debe realizarse en la planificación. Así el catálogo ofrece una entrada
explícita sin imponer una duración que sigue pendiente de decisión.

## Clave de los paralelos

El código normalizado del paralelo es único dentro del periodo. La validación
de `PeriodoAcademico.agregar_paralelo` conserva esa regla, y la persistencia
JSON actual reconstruye los paralelos buscándolos por código. Reutilizar un
código entre niveles requeriría migrar esa búsqueda a una clave compuesta antes
de relajar la unicidad; este aporte no cambia ese contrato.

## Alcance de la revisión del Builder

En el código disponible no hay una clase ni módulo `Builder`. Por eso, esta
demostración comprueba los contratos actuales de registro y construcción de
`Paralelo`, pero no atribuye al Builder una conservación de referencias que aún
no se puede verificar. Cuando se integre esa implementación, deberá comprobarse
que entregue el mismo objeto `SistemaSCHOS`, el mismo periodo y las mismas
instancias de nivel, asignatura y paralelo, y que un rechazo no deje el catálogo
en un estado parcial.

## Sección para el informe del proyecto

La integración académica usa las instancias del catálogo como referencias
compartidas: el sistema registra el periodo, el nivel y la asignatura; el nivel
contiene la asignatura; y el paralelo referencia el nivel y el periodo a los que
pertenece. El periodo solo admite paralelos cuando está abierto, y cada paralelo
debe apuntar al mismo periodo que lo registra. El escenario `2027A / Primero /
POO / paralelo A` demuestra estas relaciones con los modelos y métodos actuales.
La validación de identidad confirma que el flujo no sustituye los objetos por
copias. La revisión del Builder queda pendiente porque esa clase todavía no
aparece en el repositorio.
