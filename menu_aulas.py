"""Menú de consola para registrar y consultar aulas.

Solo interactúa con la persona usuaria: los tipos y los datos propios de
cada tipo se obtienen del servicio, de modo que un tipo de aula nuevo
aparece aquí sin modificar este archivo.
"""
from servicios.registro_aulas import ServicioRegistroAulas


def leer_booleano(mensaje):
    while True:
        texto = input(f"{mensaje} (s/n): ").strip().lower()

        if texto in ("s", "si", "sí"):
            return True
        if texto in ("n", "no"):
            return False
        print("Responde con s o n.")


def _leer_campo(campo):
    if campo.tipo == "booleano":
        return leer_booleano(campo.etiqueta)
    return input(f"{campo.etiqueta}: ")


def _registrar_aula(servicio, leer_entero):
    tipos = servicio.tipos_disponibles()

    print("\nTipos de aula:")
    for numero, creador in enumerate(tipos, start=1):
        print(f"{numero}. {creador.nombre}")

    eleccion = leer_entero("Tipo de aula: ")

    if eleccion > len(tipos):
        print("Tipo de aula no válido.")
        return

    creador = tipos[eleccion - 1]
    codigo = input("Código del aula: ").strip().upper()
    capacidad = leer_entero("Capacidad: ")
    piso = leer_entero("Piso: ", minimo=0)
    proyector = leer_booleano("¿Tiene proyector?")
    extras = {c.nombre: _leer_campo(c) for c in creador.campos_adicionales()}

    aula = servicio.registrar_aula(
        creador.clave, codigo, capacidad, piso, proyector, **extras
    )
    print(f"Aula registrada correctamente: {aula}.")


def _consultar_aulas(servicio):
    aulas = servicio.consultar_aulas()

    if not aulas:
        print("Todavía no hay aulas registradas.")
        return

    for aula in aulas:
        print(
            f"{aula.codigo_aula} | "
            f"Tipo: {aula.tipo()} | "
            f"Capacidad: {aula.capacidad} | "
            f"Piso: {aula.piso}"
        )


def menu_aulas(servicio: ServicioRegistroAulas, leer_entero):
    while True:
        print("\n--- Espacios: aulas ---")
        print("1. Registrar aula")
        print("2. Consultar aulas")
        print("0. Volver")

        opcion = leer_entero("Selecciona una opción: ", minimo=0)

        try:
            if opcion == 0:
                return
            elif opcion == 1:
                _registrar_aula(servicio, leer_entero)
            elif opcion == 2:
                _consultar_aulas(servicio)
            else:
                print("Opción no válida.")
        except (ValueError, TypeError) as error:
            print(f"No se pudo completar la operación: {error}")
