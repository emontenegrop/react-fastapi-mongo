"""Parametrización de mensajes del sistema"""

from app.schemas.errro_content_schema import ErrorContentSchema as Detail

PREFIX = "FILE"


class Messages:
    """Lista de mensajes"""

    VALIDATION_ERR = Detail(
        code=f"{PREFIX}0006",
        message="Ocurrió un error inesperado al validar los datos de entrada",
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

    RECORD_NOT_FOUND = Detail(
        code=f"{PREFIX}0001",
        message="No se encontraron resultados con los datos provistos.",
    )

    PATH_NOT_FOUND = Detail(
        code=f"{PREFIX}0003",
        message="No existe un path activo.",
    )

    VALIDATE_SIGNED_TIMEOUT = Detail(
        code=f"{PREFIX}0002",
        message="Validación de la firma electronica a tardado demasiado tiempo,"
        "porfavor intente mas tarde.",
    )

    VALIDATE_SIGNED_ERROR = Detail(
        code=f"{PREFIX}0007",
        message="Error al validar la firma electronica, porfavor intente mas tarde.",
    )

    VALIDATE_SIGNED = Detail(
        code=f"{PREFIX}0004",
        message="El documento no tiene firmas validas.",
    )

    VALIDATE_SIGNED_PROVIDER = Detail(
        code=f"{PREFIX}0005",
        message="El documento no esta firmado por el proveedor.",
    )

    INVALID_HEALTH_CHECK = Detail(
        code=f"{PREFIX}0008", message="No se pudo obtener la fecha y hora del servidor."
    )
