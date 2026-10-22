from datetime import datetime
from aplicacion import SistemaSCHOS


def leer_entero(mensaje, minimo=1):
    while True:
        try:
            valor = int(input(mensaje))

            if valor < minimo:
                print(f"Ingresa un número mayor o igual a {minimo}.")
                continue

            return valor
        except ValueError:
            print("Ingresa un número entero válido.")


def leer_fecha(mensaje):
    while True:
        texto = input(mensaje).strip()

        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            print("Ingresa una fecha válida con formato AAAA-MM-DD.")


def leer_hora(mensaje):
    while True:
        texto = input(mensaje).strip()

        try:
            return datetime.strptime(texto, "%H:%M").time()
        except ValueError:
            print("Ingresa una hora válida con formato HH:MM.")

def mostrar_resumen(sistema):
    print("\n--- Registros actuales ---")
    print(f"Usuarios: {len(sistema.usuarios)}")
    print(f"Aulas: {len(sistema.aulas)}")
    print(f"Asignaturas: {len(sistema.asignaturas)}")
    print(f"Niveles: {len(sistema.niveles)}")

    if sistema.periodo is None:
        print("Periodo: sin establecer")
    else:
        print(f"Periodo: {sistema.periodo.nombre}")


def main():
    sistema = SistemaSCHOS()

    while True:
        print("\n--- SCHOS ---")
        print("1. Recursos académicos")
        print("2. Personas y espacios")
        print("3. Planificación")
        print("4. Matrícula")
        print("5. Consultar registros")
        print("6. Guardar")
        print("0. Salir")

        opcion = leer_entero("Selecciona una opción: ", minimo=0)

        if opcion == 0:
            print("Programa cerrado.")
            break
        elif opcion == 5:
            mostrar_resumen(sistema)
        elif opcion in (1, 2, 3, 4, 6):
            print("Esta opción todavía está pendiente de implementación.")
        else:
            print("Opción no válida. Selecciona un número del 0 al 6.")


if __name__ == "__main__":
    main()