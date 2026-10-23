from datetime import datetime
from aplicacion import SistemaSCHOS
from modelos.academico.periodo_academico import PeriodoAcademico
from modelos.academico.nivel import Nivel
from modelos.academico.asignatura import Asignatura
from modelos.usuarios.docente import Docente
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.laboratorio import Laboratorio
from modelos.usuarios.estudiante import Estudiante
from modelos.academico.paralelo import Paralelo
from configuracion import JORNADAS
from servicios.gestor_horarios import GestorHorarios


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

def menu_recursos_academicos(sistema):
    while True:
        print("\n--- Recursos académicos ---")
        print("1. Crear periodo")
        print("2. Abrir periodo")
        print("3. Consultar periodo")
        print("4. Registrar nivel")
        print("5. Registrar asignatura")
        print("6. Agregar asignatura a un nivel")
        print("7. Crear paralelo")
        print("8. Consultar paralelos")
        print("0. Volver")

        opcion = leer_entero("Selecciona una opción: ", minimo=0)

        try:
            if opcion == 0:
                return

            elif opcion == 1:
                if sistema.periodo is not None:
                    print("Ya existe un periodo registrado.")
                    continue

                codigo = input("Código del periodo: ")
                nombre = input("Nombre del periodo: ")
                inicio = leer_fecha("Fecha inicial (AAAA-MM-DD): ")
                fin = leer_fecha("Fecha final (AAAA-MM-DD): ")

                periodo = PeriodoAcademico(
                    codigo, nombre, inicio, fin
                )
                sistema.establecer_periodo(periodo)
                print("Periodo registrado correctamente.")

            elif opcion == 2:
                if sistema.periodo is None:
                    print("Primero debes crear un periodo.")
                    continue

                sistema.periodo.abrir_periodo()
                print("Periodo abierto para planificación.")

            elif opcion == 3:
                if sistema.periodo is None:
                    print("Todavía no hay un periodo registrado.")
                    continue

                periodo = sistema.periodo
                print(f"Código: {periodo.codigo}")
                print(f"Nombre: {periodo.nombre}")
                print(f"Inicio: {periodo.fecha_inicio}")
                print(f"Fin: {periodo.fecha_fin}")
                print(f"Estado: {periodo.estado}")

            elif opcion == 4:
                numero = leer_entero("Número del nivel (1 a 9): ")
                nombre = input("Nombre del nivel: ")

                nivel = Nivel(numero, nombre)
                sistema.registrar_nivel(nivel)
                print("Nivel registrado correctamente.")

            elif opcion == 5:
                codigo = input("Código de la asignatura: ")
                nombre = input("Nombre de la asignatura: ")
                creditos = leer_entero("Créditos: ")
                teoricas = leer_entero("Horas teóricas: ", minimo=0)
                practicas = leer_entero("Horas prácticas: ", minimo=0)

                asignatura = Asignatura(
                    codigo, nombre, creditos, teoricas, practicas
                )
                sistema.registrar_asignatura(asignatura)
                print("Asignatura registrada correctamente.")

            elif opcion == 6:
                if not sistema.niveles or not sistema.asignaturas:
                    print("Primero registra un nivel y una asignatura.")
                    continue

                print("\nNiveles disponibles:")
                for nivel in sistema.niveles.values():
                    print(f"{nivel.numero}: {nivel.nombre}")

                numero = leer_entero("Número del nivel: ")

                if numero not in sistema.niveles:
                    print("Ese nivel no está registrado.")
                    continue

                print("\nAsignaturas disponibles:")
                for asignatura in sistema.asignaturas.values():
                    print(f"{asignatura.codigo}: {asignatura.nombre}")

                codigo = input("Código de la asignatura: ").strip().upper()

                if codigo not in sistema.asignaturas:
                    print("Esa asignatura no está registrada.")
                    continue

                nivel = sistema.niveles[numero]
                asignatura = sistema.asignaturas[codigo]
                nivel.agregar_asignatura(asignatura)

                print(f"{asignatura.nombre} agregada a {nivel.nombre}.")
                print("Asignaturas del nivel:")
                for materia in nivel.obtener_asignaturas():
                    print(f"- {materia.codigo}: {materia.nombre}")

            elif opcion == 7:
                if sistema.periodo is None:
                    print("Primero debes crear un periodo.")
                    continue

                if sistema.periodo.estado != "ABIERTO":
                    print("Primero debes abrir el periodo.")
                    continue

                if not sistema.niveles:
                    print("Primero debes registrar un nivel.")
                    continue

                print("\nNiveles disponibles:")
                for nivel in sistema.niveles.values():
                    print(f"{nivel.numero}: {nivel.nombre}")

                numero = leer_entero("Número del nivel: ")

                if numero not in sistema.niveles:
                    print("Ese nivel no está registrado.")
                    continue

                codigo = input("Código del paralelo: ").strip().upper()

                print("Jornadas:", ", ".join(JORNADAS))
                jornada = input("Jornada: ").strip().upper()
                cupo = leer_entero("Cupo máximo: ")

                paralelo = Paralelo(
                    codigo,
                    jornada,
                    cupo,
                    sistema.niveles[numero],
                    sistema.periodo,
                )

                sistema.periodo.agregar_paralelo(paralelo)
                print("Paralelo registrado correctamente.")

            elif opcion == 8:
                if sistema.periodo is None:
                    print("Primero debes crear un periodo.")
                    continue

                if not sistema.periodo.paralelos:
                    print("Todavía no hay paralelos registrados.")
                    continue

                for paralelo in sistema.periodo.paralelos:
                    print(
                        f"{paralelo.codigo} | "
                        f"Nivel: {paralelo.nivel.numero} | "
                        f"Jornada: {paralelo.jornada} | "
                        f"Inscritos: {paralelo.numero_estudiantes}/"
                        f"{paralelo.cupo_maximo}"
                    )

            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"No se pudo completar la operación: {error}")

def leer_booleano(mensaje):
    while True:
        respuesta = input(mensaje).strip().lower()

        if respuesta in ("si", "sí", "s"):
            return True
        if respuesta in ("no", "n"):
            return False

        print("Responde sí o no.")

def menu_personas_espacios(sistema):
    while True:
        print("\n--- Personas y espacios ---")
        print("1. Registrar docente")
        print("2. Consultar docentes")
        print("3. Agregar disponibilidad docente")
        print("4. Consultar disponibilidad docente")
        print("5. Registrar aula")
        print("6. Consultar aulas")
        print("7. Registrar estudiante")
        print("8. Consultar estudiantes")
        print("0. Volver")

        opcion = leer_entero("Selecciona una opción: ", minimo=0)

        try:
            if opcion == 0:
                return

            elif opcion == 1:
                nombre = input("Nombre del docente: ")
                correo = input("Correo: ")
                especialidad = input("Especialidad: ")
                maximo = leer_entero("Máximo de horas semanales: ")

                docente = Docente(
                    sistema.nuevo_id("usuario"),
                    nombre,
                    correo,
                    especialidad,
                    maximo,
                )

                sistema.registrar_usuario(docente)
                print(f"Docente registrado con ID {docente.id}.")

            elif opcion == 2:
                docentes = [
                    usuario
                    for usuario in sistema.usuarios.values()
                    if isinstance(usuario, Docente)
                ]

                if not docentes:
                    print("Todavía no hay docentes registrados.")
                    continue

                for docente in docentes:
                    print(
                        f"{docente.id}: {docente.nombre} | "
                        f"{docente.correo} | "
                        f"Máximo: {docente.max_horas_semanales} horas"
                    )

            elif opcion in (3, 4):
                docentes = [
                    usuario
                    for usuario in sistema.usuarios.values()
                    if isinstance(usuario, Docente)
                ]

                if not docentes:
                    print("Primero debes registrar un docente.")
                    continue

                for docente in docentes:
                    print(f"{docente.id}: {docente.nombre}")

                identificador = leer_entero("ID del docente: ")
                docente = sistema.usuarios.get(identificador)

                if not isinstance(docente, Docente):
                    print("El ID no corresponde a un docente registrado.")
                    continue

                if opcion == 3:
                    dia = input(
                        "Día (LUNES a VIERNES, sin tildes): "
                    ).strip().upper()
                    inicio = leer_hora("Hora inicial (HH:MM): ")
                    fin = leer_hora("Hora final (HH:MM): ")

                    docente.agregar_disponibilidad(dia, inicio, fin)
                    print("Disponibilidad registrada correctamente.")

                else:
                    if not docente.disponibilidades:
                        print("Este docente todavía no tiene disponibilidad.")
                        continue

                    for disponibilidad in docente.disponibilidades:
                        print(
                            f"{disponibilidad.dia}: "
                            f"{disponibilidad.hora_inicio:%H:%M} - "
                            f"{disponibilidad.hora_fin:%H:%M}"
                        )

            elif opcion == 5:
                print("1. Aula teórica")
                print("2. Laboratorio")
                tipo = leer_entero("Tipo de aula: ")

                if tipo not in (1, 2):
                    print("Tipo de aula no válido.")
                    continue

                codigo = input("Código del aula: ").strip().upper()
                capacidad = leer_entero("Capacidad: ")
                piso = leer_entero("Piso (0 para planta baja): ", minimo=0)
                proyector = leer_booleano("¿Tiene proyector? (sí/no): ")

                if tipo == 1:
                    aula = AulaTeorica(
                        codigo, capacidad, piso, proyector
                    )
                else:
                    equipamiento = input("Equipamiento del laboratorio: ")
                    aula = Laboratorio(
                        codigo, capacidad, piso, proyector, equipamiento
                    )

                sistema.registrar_aula(aula)
                print("Aula registrada correctamente.")

            elif opcion == 6:
                if not sistema.aulas:
                    print("Todavía no hay aulas registradas.")
                    continue

                for aula in sistema.aulas.values():
                    print(
                        f"{aula.codigo_aula} | "
                        f"Tipo: {aula.tipo()} | "
                        f"Capacidad: {aula.capacidad} | "
                        f"Piso: {aula.piso}"
                    )

            elif opcion == 7:
                nombre = input("Nombre del estudiante: ")
                correo = input("Correo: ")
                cedula = input("Cédula: ")
                carrera = input("Carrera: ")

                estudiante = Estudiante(
                    sistema.nuevo_id("usuario"),
                    nombre,
                    correo,
                    cedula,
                    carrera,
                )

                sistema.registrar_usuario(estudiante)
                print(f"Estudiante registrado con ID {estudiante.id}.")

            elif opcion == 8:
                estudiantes = [
                    usuario
                    for usuario in sistema.usuarios.values()
                    if isinstance(usuario, Estudiante)
                ]

                if not estudiantes:
                    print("Todavía no hay estudiantes registrados.")
                    continue

                for estudiante in estudiantes:
                    print(
                        f"{estudiante.id}: {estudiante.nombre} | "
                        f"{estudiante.correo} | "
                        f"Carrera: {estudiante.carrera}"
                    )

            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"No se pudo completar la operación: {error}")

def menu_planificacion(sistema):
    if sistema.periodo is None:
        print("Primero debes crear un periodo.")
        return

    gestor = GestorHorarios(sistema.periodo, sistema.aulas)

    while True:
        print("\n--- Planificación ---")
        print("1. Asignar docente y materia a un paralelo")
        print("2. Consultar asignaciones")
        print("3. Crear bloque de horario")
        print("4. Consultar horarios")
        print("5. Validar planificación")
        print("0. Volver")

        opcion = leer_entero("Selecciona una opción: ", minimo=0)

        try:
            if opcion == 0:
                return

            elif opcion == 1:
                if sistema.periodo.estado != "ABIERTO":
                    print("El periodo debe estar abierto.")
                    continue

                paralelos = {
                    paralelo.codigo: paralelo
                    for paralelo in sistema.periodo.paralelos
                }

                docentes = {
                    usuario.id: usuario
                    for usuario in sistema.usuarios.values()
                    if isinstance(usuario, Docente)
                }

                if not paralelos or not docentes:
                    print("Primero registra un paralelo y un docente.")
                    continue

                print("\nParalelos disponibles:")
                for paralelo in paralelos.values():
                    print(
                        f"{paralelo.codigo}: "
                        f"Nivel {paralelo.nivel.numero}"
                    )

                codigo = input("Código del paralelo: ").strip().upper()

                if codigo not in paralelos:
                    print("Ese paralelo no está registrado.")
                    continue

                paralelo = paralelos[codigo]
                materias = {
                    materia.codigo: materia
                    for materia in paralelo.nivel.obtener_asignaturas()
                }

                if not materias:
                    print("El nivel de ese paralelo no tiene asignaturas.")
                    continue

                print("\nAsignaturas del nivel:")
                for materia in materias.values():
                    print(f"{materia.codigo}: {materia.nombre}")

                codigo_materia = input(
                    "Código de la asignatura: "
                ).strip().upper()

                if codigo_materia not in materias:
                    print("La asignatura no pertenece a ese nivel.")
                    continue

                print("\nDocentes disponibles:")
                for docente in docentes.values():
                    print(f"{docente.id}: {docente.nombre}")

                identificador = leer_entero("ID del docente: ")

                if identificador not in docentes:
                    print("Ese ID no corresponde a un docente.")
                    continue

                asignacion = gestor.crear_asignacion(
                    sistema.nuevo_id("asignacion"),
                    docentes[identificador],
                    materias[codigo_materia],
                    paralelo,
                )

                print(
                    f"Asignación registrada con ID "
                    f"{asignacion.id_asignacion}."
                )

            elif opcion == 2:
                hay_asignaciones = False

                for paralelo in sistema.periodo.paralelos:
                    for asignacion in paralelo.asignaciones:
                        hay_asignaciones = True
                        print(
                            f"ID {asignacion.id_asignacion} | "
                            f"{asignacion.asignatura.nombre} | "
                            f"Docente: {asignacion.docente.nombre} | "
                            f"Paralelo: {paralelo.codigo} | "
                            f"Horas semanales: "
                            f"{asignacion.horas_semanales}"
                        )

                if not hay_asignaciones:
                    print("Todavía no hay asignaciones registradas.")

            elif opcion == 3:
                asignaciones = {
                    asignacion.id_asignacion: asignacion
                    for paralelo in sistema.periodo.paralelos
                    for asignacion in paralelo.asignaciones
                }

                if not asignaciones or not sistema.aulas:
                    print("Primero registra una asignación y un aula.")
                    continue

                print("\nAsignaciones disponibles:")
                for asignacion in asignaciones.values():
                    print(
                        f"{asignacion.id_asignacion}: "
                        f"{asignacion.asignatura.nombre} | "
                        f"{asignacion.docente.nombre} | "
                        f"Paralelo {asignacion.paralelo.codigo}"
                    )

                identificador = leer_entero("ID de la asignación: ")

                if identificador not in asignaciones:
                    print("Esa asignación no está registrada.")
                    continue

                print("\nAulas disponibles:")
                for aula in sistema.aulas.values():
                    print(
                        f"{aula.codigo_aula}: {aula.tipo()} | "
                        f"Capacidad: {aula.capacidad}"
                    )

                codigo = input("Código del aula: ").strip().upper()

                if codigo not in sistema.aulas:
                    print("Esa aula no está registrada.")
                    continue

                dia = input(
                    "Día (LUNES a VIERNES, sin tildes): "
                ).strip().upper()
                inicio = leer_hora("Hora inicial (HH:MM): ")
                fin = leer_hora("Hora final (HH:MM): ")
                tipo = input(
                    "Tipo de sesión (TEORIA/PRACTICA): "
                ).strip().upper()

                horario = gestor.crear_horario(
                    sistema.nuevo_id("horario"),
                    asignaciones[identificador],
                    dia,
                    inicio,
                    fin,
                    sistema.aulas[codigo],
                    tipo,
                )

                print(
                    f"Horario registrado con ID {horario.id_horario}. "
                    f"Duración: {horario.calcular_duracion()} minutos."
                )

            elif opcion == 4:
                hay_horarios = False

                for paralelo in sistema.periodo.paralelos:
                    for asignacion in paralelo.asignaciones:
                        for horario in asignacion.horarios:
                            hay_horarios = True
                            print(
                                f"ID {horario.id_horario} | "
                                f"{asignacion.asignatura.nombre} | "
                                f"{asignacion.docente.nombre} | "
                                f"Paralelo {paralelo.codigo} | "
                                f"{horario.dia} "
                                f"{horario.hora_inicio:%H:%M}-"
                                f"{horario.hora_fin:%H:%M} | "
                                f"Aula {horario.aula.codigo_aula} | "
                                f"{horario.tipo_sesion}"
                            )

                if not hay_horarios:
                    print("Todavía no hay horarios registrados.")

            elif opcion == 5:
                observaciones = gestor.validar_planificacion()

                if observaciones:
                    print("\nPendientes de la planificación:")
                    for observacion in observaciones:
                        print(f"- {observacion}")
                else:
                    print("\nLa planificación está completa según las validaciones del sistema.")

            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"No se pudo completar la operación: {error}")

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
        elif opcion == 1:
            menu_recursos_academicos(sistema)
        elif opcion == 2:
            menu_personas_espacios(sistema)
        elif opcion == 3:
            menu_planificacion(sistema)
        elif opcion in (4, 6):
            print("Esta opción todavía está pendiente de implementación.")
        else:
            print("Opción no válida. Selecciona un número del 0 al 6.")


if __name__ == "__main__":
    main()