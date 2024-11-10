from app.utils.exceptions import DetailHttpException
from fastapi import status
from app.config.messages import Messages as msg


def validate_field_int(field_name: str, field_value: object):
    """
    Validar si una variable es string
    Args:
        field_name (str): nombre del campo a validar
        field_value (object): valor del campo a validar
    Raises:
        DetailHttpException: 422, {field_name} debe ser texto valido, y distinto de vacio.
    Returns:
        true
    """
    try:
        if int(field_value) and int(field_value) > 0:  # type: ignore
            return True

    except Exception as ex:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, msg.VALIDATION_ERR_INT
        )


def validate_field_str(field_name: str, field_value: object):
    """
    Validar si una variable es string
    Args:
        field_name (str): nombre del campo a validar
        field_value (object): valor del campo a validar
    Raises:
        DetailHttpException: 422, {field_name} debe ser texto valido, y distinto de vacio.
    Returns:
        true
    """
    if str(field_value) and len(field_value) > 0 and field_value is not None:  # type: ignore
        return True
    else:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, msg.VALIDATION_ERR_STRING
        )
