import base64
import datetime
import json
import sys
import traceback
import zipfile
from io import BytesIO
from os import makedirs, remove

from app.config.messages import Messages as msg
from app.config.settings import settings
from app.db.database import db
from app.logger import logger
from app.middleware.router_error_handler import RouteErrorHandler
from app.schemas.errro_content_schema import ErrorContentSchema as Detail
from app.utils.exceptions import DetailHttpException
from app.utils.validations import (validate_field_int, validate_field_str,
                                   verificar_documento_firmado)
from bson import ObjectId  # type: ignore
from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import StreamingResponse

router = APIRouter(route_class=RouteErrorHandler)

server_path = settings.SERVER_PATH


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_description="Crear un nuevo documento y cargar el archivo",
    tags=["document_file"],
)
async def file_upload(file: UploadFile = File(...), document: str = Form()):
    try:
        now = datetime.datetime.now()
        document_json = json.loads(document.strip())
        contenido_zip = await file.read()

        # VALIDAR QUE LA INFORMACIÓN ENVIADA SEA CORRECTA
        diccionario = dict(document_json)

        # file_type_id
        validate_field_int("file_type_id", diccionario["file_type_id"])

        # aplication_id
        validate_field_str("aplication_id", diccionario["aplication_id"])

        # created_by
        validate_field_int("created_by", diccionario["created_by"])

        # person_id
        validate_field_int("person_id", diccionario["person_id"])

        # BUSCAR EL PATH ACTIVO PARA GUARDAR LOS ARCHIVOS
        active_file_path = await db.paths.find_one({"state": "ACTIVO"})
        if not active_file_path:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.PATH_NOT_FOUND)

        repo_path_active = active_file_path["path"]
        ruta = (
            f"{server_path}/{repo_path_active}/"
            f'{document_json["aplication_id"]}/{now.strftime("%Y")}/'
            f'{now.strftime("%m")}/{now.strftime("%d")}/'
            f'{document_json["file_type_id"]}/'
        )
        makedirs(ruta, exist_ok=True)

        document_json["file_name"] = file.filename
        document_json["file_url"] = ruta
        document_json["active"] = True
        document_json["created_at"] = now
        document_json["block"] = False

        new_document_file = await db.files.insert_one(document_json)
        document_get = await db.files.find_one({"_id": new_document_file.inserted_id})
        document_get["id"] = str(document_get["_id"])  # type: ignore
        del document_get["_id"]  # type: ignore

        with zipfile.ZipFile(
            ruta + str(document_get["id"]) + ".zip", "w"  # type: ignore
        ) as archivo_zip:
            archivo_zip.writestr(
                str(file.filename),
                contenido_zip,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
            archivo_zip.close

        return document_get
    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.get(
    "/{person_id}/{aplication_id}/{file_type_id}",
    status_code=status.HTTP_200_OK,
    response_description="Listar todos los documentos de la persona",
    tags=["document_file"],
)
async def get_documents_by_type(person_id: int, aplication_id: str, file_type_id: str):
    """
    <b>Listar Archivos filtrados por persona, aplicacion, tipo de archivo</b>\n
    Args:
    -   file_type_id (str: Form): Identificador de tipo de archivo(debe ser enviado
        como lista de numeros sin espacios, separado con " , ")\n
    Raises:
    -   DetailHttpException: 404, No se encontró registros
    -   DetailHttpException: 500, Un error ha ocurrido, por favor intente mas
        tarde.(Todas las posibles excepciones no controladas)
    Returns:
    -   dict -> File
    """
    try:
        types_in = []
        type_list = file_type_id.split(",")

        for type_file in type_list:
            types_in.append(int(type_file))

        documents_list = []
        documents = list(
            await db.files.find(
                {
                    "aplication_id": aplication_id,
                    "person_id": person_id,
                    "file_type_id": {"$in": types_in},
                }
            ).to_list()
        )

        if not documents:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND)

        for document in documents:
            document["id"] = str(document["_id"])
            del document["_id"]
            documents_list.append(document)

        return documents_list

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR,
        )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_description="Descargar un documento",
    tags=["document_file"],
)
async def download_document(id: str):
    """
    <b>Descargar un documento descomprimido</b>\n
    Args:
    -   id (str, Form): Identificador del archivo

    Raises:
    -   DetailHttpException: 404, No existe el documento
    -   DetailHttpException: 500, Un error ha ocurrido, por favor intente mas tarde.\n

    Returns:
    -   file - ContenType
    """
    try:
        search_document_file =await db.files.find_one({"_id": ObjectId(id)})
        if not search_document_file:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND)

        path = f'{search_document_file["file_url"]}{id}.zip'
        # Crear un objeto BytesIO en memoria para guardar el contenido del archivo zip
        file_buffr = BytesIO()

        # Leer el contenido del archivo zip en memoria
        with zipfile.ZipFile(path) as zip_file:
            for name in zip_file.namelist():
                with zip_file.open(name) as zipped_file:
                    file_buffr.write(zipped_file.read())

        # Crear una respuesta de streaming para enviar el contenido del archivo zip al navegador
        file_buffr.seek(0)
        return StreamingResponse(
            file_buffr,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename={search_document_file["file_name"]}'
            },
        )
    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR,
        )


@router.get(
    "/data/{id}",
    status_code=status.HTTP_200_OK,
    response_description="Ver datos del documento por ID",
    tags=["document_file"],
)
async def get_document_by_id(id: str):
    """
    <b>Ver datos del documento</b>\n
    Raises:
    -   DetailHttpException: 422, 001 No existe el documento
    -   DetailHttpException: 500, 000 Un error ha ocurrido, por favor intente mas tarde.\n
    Returns:
    -   document -> dict
    """
    try:

        search_document_by_id = await db.files.find_one({"_id": ObjectId(id)})

        if not search_document_by_id:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND)

        search_document_by_id.update({"_id": str(search_document_by_id["_id"])})

        return search_document_by_id

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}") # type: ignore
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_description="Actualizar el estado (block) de un documento",
    tags=["document_file"],
)
async def document_update(id: str, document: dict):
    """
    <b>Actualizar el estado (block) del documento</b>\n
    <b>Obligatorio:
    -   {"block": true}</b>\n
    Args:
    -   document -> dict (block) -> True/False,  -> "campo que identifica si un archivo
    es borrable  no (True) o si (False), por defecto False"\n
    Raises:
    -   DetailHttpException: 422, El parametro (block) enviado no es correcto.
    -   DetailHttpException: 500, Un error ha ocurrido, por favor intente mas tarde.\n
    Returns:
    -   document -> dict
    """
    try:
        if document["block"] is not True and document["block"] is not False:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                Detail(
                    code=msg.VALIDATION_ERR.code,
                    message=f"{msg.VALIDATION_ERR.message}, el parametro (block) enviado no es correcto",
                ),
            )
        
        existing_path = await db.files.find_one({"_id": ObjectId(id)})
        if not existing_path:
            raise DetailHttpException(
                status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND
            )
                   
        # Actualizamos el documento
        updated_file_document = await db.files.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": document}
        )

        # Recuperamos la información actualizada
        #updated_file_document = db.files.find_one({"_id": ObjectId(id)})

        updated_file_document["id"] = str(updated_file_document["_id"])
        del updated_file_document["_id"]

        return updated_file_document

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR,
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_description="Documento Eliminado",
    tags=["document_file"],
)
async def document_detele(id: str):
    """
    <b>Eliminar documento y el archivo fisicamente</b>\n
    Raises:
    -   DetailHttpException: 422, No existe el documento
    -   DetailHttpException: 500, Un error ha ocurrido, por favor intente mas tarde.\n
    Returns:
    -   document -> dict
    """
    try:
        search_document_file = await db.files.find_one({"_id": ObjectId(id)})
        if not search_document_file:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND)

        path = f'{search_document_file["file_url"]}{id}.zip'
        remove(path)
        deleted_file_document = await db.files.find_one_and_delete({"_id": ObjectId(id)})

        deleted_file_document["id"] = str(deleted_file_document["_id"])
        del deleted_file_document["_id"]
        return deleted_file_document

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.get(
    "/{person_id}/{aplication_id}",
    status_code=status.HTTP_200_OK,
    response_description="Listar todos los documentos de la persona",
    tags=["document_file"],
)
async def get_documents(person_id: int, aplication_id: str):
    """
    <b>Listar Archivos filtrados por persona y aplicacion</b>\n
    Raises:
    -   DetailHttpException: 422, No se encontró registros.
    -   DetailHttpExceotion: 500, Un error ha ocurrido, por favor intente mas tarde.\n
    Returns:
    -   document -> dict
    """
    try:
        documents_list = []
        documents = list(
            await db.files.find(
                {
                    "aplication_id": aplication_id,
                    "person_id": person_id,
                }
            ).to_list()
        )

        if not documents:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND)

        for document in documents:
            document["id"] = str(document["_id"])
            del document["_id"]
            documents_list.append(document)

        return documents_list

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.post(
    "/signed_validate/",
    status_code=status.HTTP_200_OK,
    response_description="Cargar un nuevo documento, validar firma y cargar el archivo",
    tags=["document_file"],
)
async def upload_file_signed(
    file: UploadFile, document: str = Form(), cedula_ruc: str = Form()
):
    try:
        now = datetime.datetime.now()
        document_json = json.loads(document.strip())
        contenido_zip = await file.read()
        logger.debug(document_json)
        logger.debug(cedula_ruc)

        # VALIDAR QUE LA INFORMACIÓN ENVIADA SEA CORRECTA
        diccionario = dict(document_json)

        # file_type_id
        validate_field_int("file_type_id", diccionario["file_type_id"])

        # aplication_id
        validate_field_str("aplication_id", diccionario["aplication_id"])

        # created_by
        validate_field_int("created_by", diccionario["created_by"])

        # person_id
        validate_field_int("person_id", diccionario["person_id"])

        # BUSCAR EL PATH ACTIVO PARA GUARDAR LOS ARCHIVOS
        active_file_path = await db.paths.find_one({"state": "ACTIVO"})
        if not active_file_path:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, msg.PATH_NOT_FOUND
            )

        repo_path_active = active_file_path["path"]
        ruta = (
            f'{server_path}/{repo_path_active}/{document_json["aplication_id"]}'
            f'/{now.strftime("%Y")}/{now.strftime("%m")}/{now.strftime("%d")}'
            f'/{document_json["file_type_id"]}/'
        )
        makedirs(ruta, exist_ok=True)

        # TRANSFORMAR EL ARCHIVO A BASE64
        documento_base64 = base64.b64encode(contenido_zip)
        result_signed = verificar_documento_firmado(documento_base64)

        # FIRMAS VALIDAS
        json_signed = json.loads(result_signed)  # type: ignore

        if not json_signed["firmasValidas"]:
            raise DetailHttpException(
                422,
                msg.VALIDATE_SIGNED,
            )

        identity = 0
        for certify in json_signed["certificado"]:
            if (
                certify["cedula"] == cedula_ruc.strip()
                or certify["cedula"] == cedula_ruc.strip()[0:10]
            ):
                identity = identity + 1

        if identity == 0:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, msg.VALIDATE_SIGNED_PROVIDER
            )

        document_json["file_name"] = file.filename
        document_json["file_url"] = ruta
        document_json["active"] = True
        document_json["created_at"] = now
        document_json["block"] = False
        document_json["signed"] = json_signed

        new_document_file = await db.files.insert_one(document_json)
        document_get = await db.files.find_one({"_id": new_document_file.inserted_id})
        document_get["id"] = str(document_get["_id"])  # type: ignore
        del document_get["_id"]  # type: ignore

        with zipfile.ZipFile(
            ruta + str(document_get["id"]) + ".zip", "w"  # type: ignore
        ) as archivo_zip:
            archivo_zip.writestr(
                str(file.filename),
                contenido_zip,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
            archivo_zip.close

        return document_get
    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )