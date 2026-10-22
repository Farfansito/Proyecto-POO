from modelos.aulas.aula import Aula


class AulaTeorica(Aula):
    def tipo(self) -> str:
        return "TEORICA"

    def admite(self, tipo_sesion: str) -> bool:
        return tipo_sesion == "TEORIA"