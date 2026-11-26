"""Guardado y recuperación íntegra del estado de SCHOS en formato JSON."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import date, time
from pathlib import Path

from aplicacion import SistemaSCHOS
from modelos.academico.asignatura import Asignatura
from modelos.academico.matricula import Matricula
from modelos.academico.nivel import Nivel
from modelos.academico.paralelo import Paralelo
from modelos.academico.periodo_academico import PeriodoAcademico
from modelos.aulas.auditorio import Auditorio
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.laboratorio import Laboratorio
from modelos.aulas.sala_sustentacion import SalaSustentacion
from modelos.usuarios.administrador import Administrador
from modelos.usuarios.docente import Docente
from modelos.usuarios.estudiante import Estudiante
from servicios.gestor_horarios import GestorHorarios


_VERSION = 1
_ENTIDADES_ID = ("usuario", "asignacion", "horario", "matricula")
_CAMPOS_CONTADOR = frozenset(_ENTIDADES_ID)


class AlmacenJSON:
    """Persiste un periodo y sus relaciones usando identificadores estables."""

    def __init__(self, ruta="datos/schos.json"):
        self.ruta = Path(ruta)

    def guardar(self, sistema: SistemaSCHOS) -> None:
        if not isinstance(sistema, SistemaSCHOS):
            raise ValueError("Solo se puede guardar un SistemaSCHOS.")

        datos = self._serializar(sistema)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.ruta.parent,
                prefix=f".{self.ruta.name}.",
                suffix=".tmp",
                delete=False,
            ) as archivo:
                temporal = Path(archivo.name)
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
                archivo.write("\n")
                archivo.flush()
                os.fsync(archivo.fileno())

            if self.ruta.exists():
                respaldo = self.ruta.with_suffix(self.ruta.suffix + ".bak")
                respaldo_temporal = None

                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb",
                        dir=self.ruta.parent,
                        prefix=f".{respaldo.name}.",
                        suffix=".tmp",
                        delete=False,
                    ) as copia:
                        respaldo_temporal = Path(copia.name)
                        with self.ruta.open("rb") as anterior:
                            shutil.copyfileobj(anterior, copia)
                        copia.flush()
                        os.fsync(copia.fileno())

                    os.replace(respaldo_temporal, respaldo)

                except OSError:
                    if respaldo_temporal is not None:
                        respaldo_temporal.unlink(missing_ok=True)
                    raise

            os.replace(temporal, self.ruta)

        except OSError:
            if temporal is not None:
                temporal.unlink(missing_ok=True)
            raise

    def cargar(self) -> SistemaSCHOS:
        """Carga los datos; si no existe el archivo, inicia un sistema vacío."""
        if not self.ruta.exists():
            return SistemaSCHOS()

        try:
            with self.ruta.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError(
                f"El archivo de datos no contiene JSON válido: {error}"
            ) from error
        except OSError:
            raise

        self._validar_formato(datos)

        try:
            return self._reconstruir(datos)
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                f"No se pudieron recuperar los datos de SCHOS: {error}"
            ) from error

    @staticmethod
    def _serializar(sistema: SistemaSCHOS) -> dict:
        aulas = []

        for aula in sistema.aulas.values():
            registro = {
                "tipo": aula.tipo(),
                "codigo": aula.codigo_aula,
                "capacidad": aula.capacidad,
                "piso": aula.piso,
                "tiene_proyector": aula.tiene_proyector,
            }

            if isinstance(aula, Laboratorio):
                registro["equipamiento"] = aula.equipamiento
            elif isinstance(aula, Auditorio):
                registro["tiene_sonido"] = aula.tiene_sonido
            elif isinstance(aula, SalaSustentacion):
                registro["tiene_grabacion"] = aula.tiene_grabacion

            aulas.append(registro)

        usuarios = []

        for usuario in sistema.usuarios.values():
            registro = {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
            }

            if isinstance(usuario, Docente):
                registro.update(
                    tipo="DOCENTE",
                    especialidad=usuario.especialidad,
                    max_horas_semanales=usuario.max_horas_semanales,
                    disponibilidades=[
                        {
                            "dia": disponibilidad.dia,
                            "hora_inicio": disponibilidad.hora_inicio.strftime(
                                "%H:%M"
                            ),
                            "hora_fin": disponibilidad.hora_fin.strftime(
                                "%H:%M"
                            ),
                        }
                        for disponibilidad in usuario.disponibilidades
                    ],
                )
            elif isinstance(usuario, Estudiante):
                registro.update(
                    tipo="ESTUDIANTE",
                    cedula=usuario.cedula,
                    carrera=usuario.carrera,
                )
            elif isinstance(usuario, Administrador):
                registro.update(
                    tipo="ADMINISTRADOR",
                    rol=usuario.rol,
                )
            else:
                raise ValueError(
                    f"Tipo de usuario no compatible: "
                    f"{type(usuario).__name__}."
                )

            usuarios.append(registro)

        asignaturas = [
            {
                "codigo": asignatura.codigo,
                "nombre": asignatura.nombre,
                "creditos": asignatura.creditos,
                "horas_teoricas": asignatura.horas_teoricas,
                "horas_practicas": asignatura.horas_practicas,
                "descripcion": asignatura.descripcion,
            }
            for asignatura in sistema.asignaturas.values()
        ]

        niveles = [
            {
                "numero": nivel.numero,
                "nombre": nivel.nombre,
                "asignaturas": [
                    asignatura.codigo
                    for asignatura in nivel.obtener_asignaturas()
                ],
            }
            for nivel in sistema.niveles.values()
        ]

        periodo = None

        if sistema.periodo is not None:
            periodo = {
                "codigo": sistema.periodo.codigo,
                "nombre": sistema.periodo.nombre,
                "fecha_inicio": sistema.periodo.fecha_inicio.isoformat(),
                "fecha_fin": sistema.periodo.fecha_fin.isoformat(),
                "estado": sistema.periodo.estado,
                "paralelos": [],
            }

            for paralelo in sistema.periodo.paralelos:
                paralelo_datos = {
                    "codigo": paralelo.codigo,
                    "jornada": paralelo.jornada,
                    "cupo_maximo": paralelo.cupo_maximo,
                    "nivel": paralelo.nivel.numero,
                    "asignaciones": [],
                }

                for asignacion in paralelo.asignaciones:
                    asignacion_datos = {
                        "id": asignacion.id_asignacion,
                        "docente": asignacion.docente.id,
                        "asignatura": asignacion.asignatura.codigo,
                        "horarios": [],
                    }

                    for horario in asignacion.horarios:
                        asignacion_datos["horarios"].append(
                            {
                                "id": horario.id_horario,
                                "dia": horario.dia,
                                "hora_inicio": horario.hora_inicio.strftime(
                                    "%H:%M"
                                ),
                                "hora_fin": horario.hora_fin.strftime(
                                    "%H:%M"
                                ),
                                "aula": horario.aula.codigo_aula.strip().upper(),
                                "tipo_sesion": horario.tipo_sesion,
                            }
                        )

                    paralelo_datos["asignaciones"].append(asignacion_datos)

                periodo["paralelos"].append(paralelo_datos)

        matriculas = []

        for usuario in sistema.usuarios.values():
            if not isinstance(usuario, Estudiante):
                continue

            for matricula in usuario.matriculas:
                matriculas.append(
                    {
                        "id": matricula.id_matricula,
                        "estudiante": usuario.id,
                        "fecha": matricula.fecha.isoformat(),
                        "estado": matricula.estado,
                        "paralelo": (
                            matricula.paralelo.codigo
                            if matricula.paralelo is not None
                            else None
                        ),
                    }
                )

        return {
            "version": _VERSION,
            "usuarios": usuarios,
            "aulas": aulas,
            "asignaturas": asignaturas,
            "niveles": niveles,
            "periodo": periodo,
            "matriculas": matriculas,
            "siguientes_ids": dict(sistema.siguientes_ids),
        }

    @staticmethod
    def _validar_formato(datos) -> None:
        if not isinstance(datos, dict):
            raise ValueError("La raíz del archivo debe ser un objeto JSON.")

        if type(datos.get("version")) is not int or datos["version"] != _VERSION:
            raise ValueError(
                f"Versión de datos no compatible: {datos.get('version')!r}."
            )

        for clave in (
            "usuarios",
            "aulas",
            "asignaturas",
            "niveles",
            "matriculas",
        ):
            if not isinstance(datos.get(clave), list):
                raise ValueError(f"El campo {clave!r} debe ser una lista.")

        if datos.get("periodo") is not None and not isinstance(
            datos["periodo"], dict
        ):
            raise ValueError("El campo 'periodo' debe ser un objeto o null.")

        contadores = datos.get("siguientes_ids")

        if (
            not isinstance(contadores, dict)
            or set(contadores) != _CAMPOS_CONTADOR
        ):
            raise ValueError(
                "Los contadores siguientes_ids no tienen las claves requeridas."
            )

        if any(
            type(valor) is not int or valor < 1
            for valor in contadores.values()
        ):
            raise ValueError("Los siguientes IDs deben ser enteros positivos.")

    @staticmethod
    def _reconstruir(datos) -> SistemaSCHOS:
        sistema = SistemaSCHOS()

        for registro in datos["aulas"]:
            tipo = registro["tipo"]
            comunes = (
                registro["codigo"],
                registro["capacidad"],
                registro["piso"],
                registro["tiene_proyector"],
            )

            if tipo == "TEORICA":
                aula = AulaTeorica(*comunes)
            elif tipo == "LABORATORIO":
                aula = Laboratorio(*comunes, registro["equipamiento"])
            elif tipo == "AUDITORIO":
                aula = Auditorio(*comunes, registro["tiene_sonido"])
            elif tipo == "SUSTENTACION":
                aula = SalaSustentacion(
                    *comunes,
                    registro["tiene_grabacion"],
                )
            else:
                raise ValueError(f"Tipo de aula desconocido: {tipo!r}.")

            sistema.registrar_aula(aula)

        for registro in datos["usuarios"]:
            tipo = registro["tipo"]
            comunes = (
                registro["id"],
                registro["nombre"],
                registro["correo"],
            )

            if tipo == "DOCENTE":
                usuario = Docente(
                    *comunes,
                    registro["especialidad"],
                    registro["max_horas_semanales"],
                )

                for disponibilidad in registro["disponibilidades"]:
                    usuario.agregar_disponibilidad(
                        disponibilidad["dia"],
                        time.fromisoformat(disponibilidad["hora_inicio"]),
                        time.fromisoformat(disponibilidad["hora_fin"]),
                    )

            elif tipo == "ESTUDIANTE":
                usuario = Estudiante(
                    *comunes,
                    registro["cedula"],
                    registro["carrera"],
                )

            elif tipo == "ADMINISTRADOR":
                usuario = Administrador(
                    *comunes,
                    registro["rol"],
                )

            else:
                raise ValueError(f"Tipo de usuario desconocido: {tipo!r}.")

            sistema.registrar_usuario(usuario)

        for registro in datos["asignaturas"]:
            sistema.registrar_asignatura(
                Asignatura(
                    registro["codigo"],
                    registro["nombre"],
                    registro["creditos"],
                    registro["horas_teoricas"],
                    registro["horas_practicas"],
                    registro["descripcion"],
                )
            )

        for registro in datos["niveles"]:
            nivel = Nivel(registro["numero"], registro["nombre"])
            sistema.registrar_nivel(nivel)

            for codigo in registro["asignaturas"]:
                try:
                    nivel.agregar_asignatura(sistema.asignaturas[codigo])
                except KeyError as error:
                    raise ValueError(
                        f"Asignatura referenciada no existe: {codigo!r}."
                    ) from error

        matriculas = datos["matriculas"]
        periodo_datos = datos["periodo"]

        if periodo_datos is None:
            if matriculas:
                raise ValueError(
                    "Hay matrículas guardadas sin periodo académico."
                )

        else:
            periodo = PeriodoAcademico(
                periodo_datos["codigo"],
                periodo_datos["nombre"],
                date.fromisoformat(periodo_datos["fecha_inicio"]),
                date.fromisoformat(periodo_datos["fecha_fin"]),
            )
            sistema.establecer_periodo(periodo)

            estado_guardado = periodo_datos["estado"]

            if estado_guardado not in (
                PeriodoAcademico.PLANIFICADO,
                PeriodoAcademico.ABIERTO,
                PeriodoAcademico.CERRADO,
            ):
                raise ValueError(
                    f"Estado de periodo desconocido: {estado_guardado!r}."
                )

            if estado_guardado in (
                PeriodoAcademico.ABIERTO,
                PeriodoAcademico.CERRADO,
            ):
                periodo.abrir_periodo()

            niveles_por_numero = sistema.niveles

            for registro in periodo_datos["paralelos"]:
                try:
                    nivel = niveles_por_numero[registro["nivel"]]
                except KeyError as error:
                    raise ValueError(
                        f"Nivel referenciado no existe: "
                        f"{registro['nivel']!r}."
                    ) from error

                paralelo = Paralelo(
                    registro["codigo"],
                    registro["jornada"],
                    registro["cupo_maximo"],
                    nivel,
                    periodo,
                )
                periodo.agregar_paralelo(paralelo)

            gestores = GestorHorarios(periodo, sistema.aulas)
            paralelos = {
                paralelo.codigo: paralelo
                for paralelo in periodo.paralelos
            }

            for registro_paralelo in periodo_datos["paralelos"]:
                paralelo = paralelos[
                    registro_paralelo["codigo"].strip().upper()
                ]

                for registro_asignacion in registro_paralelo["asignaciones"]:
                    try:
                        docente = sistema.usuarios[
                            registro_asignacion["docente"]
                        ]
                        asignatura = sistema.asignaturas[
                            registro_asignacion["asignatura"]
                        ]
                    except KeyError as error:
                        raise ValueError(
                            f"Referencia de asignación inexistente: {error}."
                        ) from error

                    if not isinstance(docente, Docente):
                        raise ValueError(
                            "Una asignación debe referenciar un docente."
                        )

                    asignacion = gestores.crear_asignacion(
                        registro_asignacion["id"],
                        docente,
                        asignatura,
                        paralelo,
                    )

                    for registro_horario in registro_asignacion["horarios"]:
                        try:
                            aula = sistema.aulas[
                                registro_horario["aula"].strip().upper()
                            ]
                        except KeyError as error:
                            raise ValueError(
                                "Aula referenciada no existe: "
                                f"{registro_horario['aula']!r}."
                            ) from error

                        gestores.crear_horario(
                            registro_horario["id"],
                            asignacion,
                            registro_horario["dia"],
                            time.fromisoformat(
                                registro_horario["hora_inicio"]
                            ),
                            time.fromisoformat(
                                registro_horario["hora_fin"]
                            ),
                            aula,
                            registro_horario["tipo_sesion"],
                        )

            estudiantes = {
                usuario.id: usuario
                for usuario in sistema.usuarios.values()
                if isinstance(usuario, Estudiante)
            }
            ids_matriculas = set()

            for registro in sorted(
                matriculas,
                key=lambda item: item["id"],
            ):
                id_matricula = registro["id"]

                if id_matricula in ids_matriculas:
                    raise ValueError(
                        f"ID de matrícula duplicado: {id_matricula!r}."
                    )
                ids_matriculas.add(id_matricula)

                try:
                    estudiante = estudiantes[registro["estudiante"]]
                except KeyError as error:
                    raise ValueError(
                        "El estudiante de la matrícula no existe: "
                        f"{registro['estudiante']!r}."
                    ) from error

                estado = registro["estado"]
                codigo_paralelo = registro["paralelo"]
                paralelo = None

                if codigo_paralelo is not None:
                    try:
                        paralelo = paralelos[codigo_paralelo.strip().upper()]
                    except KeyError as error:
                        raise ValueError(
                            "El paralelo de la matrícula no existe: "
                            f"{codigo_paralelo!r}."
                        ) from error

                if estado == "CANCELADA":
                    matricula = Matricula(
                        id_matricula,
                        estudiante,
                        periodo,
                    )
                    matricula.paralelo = paralelo
                    matricula.estado = estado
                    estudiante._matriculas.append(matricula)

                elif estado in ("PENDIENTE", "CONFIRMADA"):
                    matricula = estudiante.solicitar_matricula(
                        periodo,
                        id_matricula,
                    )

                    if paralelo is not None:
                        matricula.agregar_paralelo(paralelo)
                    elif estado == "CONFIRMADA":
                        raise ValueError(
                            "Una matrícula confirmada debe tener un paralelo."
                        )

                    if estado == "CONFIRMADA":
                        matricula.confirmar()

                else:
                    raise ValueError(
                        f"Estado de matrícula desconocido: {estado!r}."
                    )

                matricula.fecha = date.fromisoformat(registro["fecha"])

            periodo.estado = estado_guardado

        sistema.siguientes_ids = AlmacenJSON._contadores_seguros(
            datos["siguientes_ids"],
            sistema,
        )
        return sistema

    @staticmethod
    def _contadores_seguros(guardados: dict, sistema: SistemaSCHOS) -> dict:
        maximos = {clave: 0 for clave in _ENTIDADES_ID}

        if sistema.usuarios:
            maximos["usuario"] = max(sistema.usuarios)

        if sistema.periodo is not None:
            for paralelo in sistema.periodo.paralelos:
                for asignacion in paralelo.asignaciones:
                    maximos["asignacion"] = max(
                        maximos["asignacion"],
                        asignacion.id_asignacion,
                    )

                    for horario in asignacion.horarios:
                        maximos["horario"] = max(
                            maximos["horario"],
                            horario.id_horario,
                        )

        for usuario in sistema.usuarios.values():
            if isinstance(usuario, Estudiante):
                for matricula in usuario.matriculas:
                    maximos["matricula"] = max(
                        maximos["matricula"],
                        matricula.id_matricula,
                    )

        return {
            clave: max(guardados[clave], maximos[clave] + 1)
            for clave in _ENTIDADES_ID
        }