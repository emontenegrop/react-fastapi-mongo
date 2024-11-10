import datetime

from app.db.database import db
from app.logger import logger
from app.utils.exceptions import DetailHttpException
from app.utils.validations import validate_field_str
from fastapi import APIRouter, status
from app.config.messages import Messages as msg
import traceback

router = APIRouter()


@router.post(
    "/log_data/",
    tags=["log_data"],
)
async def log_data(document: dict):
    """
    <b>Subir un registro de Error</b>\n
    - {}
    <b>Campos Obligatorios
    -   {"timestamp":"04/01/2024 09:17:49","application_code":"archivos","status":"failure / success","event_id":"2213812294562653681","error":{"status_code":402,"description":"ERROR:"}}</b> \n
        Raises:
        -   DetailHttpException: 500, Un error ha ocurrido, por favor intente mas tarde.
        Returns:
    -   document -> dict
    """
    try:
        now = datetime.datetime.now()

        # VALIDAR QUE LA INFORMACIÓN ENVIADA SEA CORRECTA
        diccionario = document
        validate_field_str("application_code", diccionario["application_code"])

        # aplication_code
        validate_field_str("status", diccionario["status"])

        # user_id
        validate_field_str("event_id", diccionario["event_id"])

        # validar el error
        if diccionario["status"] == "failure":
            validate_field_str("error", diccionario["error"])

        document["created_at"] = now
        document["timestamp"] = datetime.datetime.strptime(
            document["timestamp"], "%d/%m/%Y %H:%M:%S"
        )

        await db.log_data.insert_one(document)

        return {"ok"}

    except DetailHttpException as dexc:
        # Enviar correo electronico al administrador
        # Modulo de notificaciones
        logger.debug(f"{traceback.format_exc()}")
        # raise dexc

    except Exception as exc:
        # Enviar correo electronico al administrador
        # Modulo de notificaciones
        logger.debug(f"{traceback.format_exc()}")


@router.get(
    "/log_data/{event_id}",
    status_code=status.HTTP_200_OK,
    response_description="Listar todos los logs por event_id",
    tags=["log_data"],
)
async def get_log_data(event_id: str):
    """
    <b>Listar Archivos filtrados por persona y aplicacion</b>\n
    Raises:
    -   DetailHttpException: 422, 001 No se encontró registros.
    -   DetailHttpExceotion: 500, 000 Un error ha ocurrido, por favor intente mas tarde.\n
    Returns:
    -   document -> dict
    """
    try:
        documents_list = []
        documents = list(
            await db.log_data.find(
                {"event_id": event_id},
                {
                    "application_code": 1,
                    "status": 1,
                    "error.status_code": 1,
                    "timestamp": 1,
                    "actor.client": 1,
                    "actor.api_path": 1,
                },
            ).sort({"timestamp": 1}).to_list()
        )

        if not documents:
            raise DetailHttpException(
                status.HTTP_404_NOT_FOUND,
                msg.RECORD_NOT_FOUND,
            )

        for document in documents:
            document["id"] = str(document["_id"])
            del document["_id"]
            documents_list.append(document)

        return documents_list

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        # return dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()} {exc}")
        # raise DetailHttpException(
        #    status.HTTP_500_INTERNAL_SERVER_ERROR,
        #    msg.API_UNEXPECTED_ERROR,
        # )
