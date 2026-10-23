"""Validaciones compartidas por los modelos académicos."""


def texto_no_vacio(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} debe ser un texto no vacío")


def entero(valor, campo, minimo):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ValueError(f"{campo} debe ser un entero mayor o igual a {minimo}")
