"""Parametrización de mensajes del sistema"""

from app.schemas.errro_content_schema import ErrorContentSchema as Detail

PREFIX = "LOGG"


class Messages:

    RECORD_NOT_FOUND = Detail(
        code=f"{PREFIX}0001",
        message="No se encontraron resultados con los datos provistos.",
    )

    API_UNEXPECTED_ERROR = Detail(
        code=f"{PREFIX}0000",
        message="Ocurrió un error inesperado",
    )

    # SOLO messages
    INVALID_DETAIL = (
        "La estructura del detalle de la excepción HTTP es inválida, "
        "por favor contacte a un desarrollador."
    )
    
    VALIDATION_ERR_STRING = Detail(
        code=f"{PREFIX}0002",
        message="Debe ser texto valido, y distinto de vacio.",
    )
    
    VALIDATION_ERR_INT = Detail(
        code=f"{PREFIX}0003",
        message="Debe ser numérico.",
    )

    INVALID_HEALTH_CHECK = Detail(
        code=f"{PREFIX}0004", message="No se pudo obtener la fecha y hora del servidor."
    )