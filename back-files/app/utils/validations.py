import sys

import httpx
from app.config.settings import settings
from app.logger import logger
from app.utils.exceptions import DetailHttpException
from requests.exceptions import ConnectTimeout, RequestException
from fastapi import status
from app.config.messages import Messages as msg
from app.schemas.errro_content_schema import ErrorContentSchema as Detail


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
        else:
            raise ValueError()
    except Exception as ex:
        ex_type, ex_obj, tb = sys.exc_info()
        logger.debug(f"L[{tb.tb_lineno}] {ex}")  # type: ignore
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code=msg.VALIDATION_ERR.code,
                message=f"{msg.VALIDATION_ERR.message} {field_name} debe ser numérico.",
            ),
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
    try:
        if str(field_value) and len(field_value) > 0 and field_value is not None:  # type: ignore
            return True
        else:
            raise ValueError()
    except Exception as ex:
        ex_type, ex_obj, tb = sys.exc_info()
        logger.debug(f"L[{tb.tb_lineno}] {ex}")  # type: ignore
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code=msg.VALIDATION_ERR.code,
                message=f"{msg.VALIDATION_ERR.message} {field_name} debe ser texto valido, y distinto de vacio.",
            ),
        )


def verificar_documento_firmado(documento_base64):
    """
    Validamos las firmas del documento utilizando FIRMAEC
    """

    response = None
    response_backup = None
    header = {"Content-Type": "text/plain; charset=UTF-8"}

    try:
        response = httpx.post(
            url=str(settings.WS_VALIDACION_FIRMA),
            data=documento_base64.decode("utf-8"),
            headers=header,
            timeout=settings.TIMEOUT,
        )
    except Exception as err:
        ex_type, ex_obj, tb = sys.exc_info()
        logger.debug(f"L[{tb.tb_lineno}] {err}")  # type: ignore

    if response:
        return response.text

        # Si no hay respuesta del ws, consultamos info en el backup
    try:
        response_backup = httpx.post(
            url=str(settings.WS_VALIDACION_FIRMA),
            data=documento_base64.decode("utf-8"),
            headers=header,
            timeout=settings.TIMEOUT * 3,
        )
    except ConnectTimeout as err:
        ex_type, ex_obj, tb = sys.exc_info()
        logger.debug(f"L[{tb.tb_lineno}] {err}")  # type: ignore
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, msg.VALIDATE_SIGNED_TIMEOUT
        )
    except RequestException as err:
        ex_type, ex_obj, tb = sys.exc_info()
        logger.debug(f"L[{tb.tb_lineno}] {err}")  # type: ignore
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, msg.VALIDATE_SIGNED_ERROR
        )

    if response_backup:
        return response_backup.text

    return None
