import datetime
import traceback

from app.config.messages import Messages as msg
from app.db.database import db
from app.logger import logger
from app.middleware.router_error_handler import RouteErrorHandler
from app.models.file_path import FilePath, UpdateFilePath
from app.utils.exceptions import DetailHttpException
from bson import ObjectId
from fastapi import APIRouter, Request, status

router = APIRouter(route_class=RouteErrorHandler)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_description="Listar path de archivos",
    tags=["file_path"],
)
async def get_file_path(request: Request):
    """
    <b>Listar todos los FilePath existentes en la base de datos</b> \n
    Raises: \n
    -   DetailHttpException: 500 \n
    Returns: \n
    -   _type_: List[FilPath]\n
    """
    try:
        file_paths = []
        paths = list(await db.paths.find().to_list())
        for path in paths:
            path["id"] = str(path["_id"])
            del path["_id"]
            file_paths.append(path)
        return file_paths
    except DetailHttpException as dexc:        
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:       
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Listar path de archivos",
    tags=["file_path"],
)
async def create_file_path(file_path: FilePath):
    """
    <b>Crear un documento FilePath</b>\n
    Args:\n
    -   file_path (FilePath, optional): Modelo a ser creado.\n
    Raises:\n
    -   DetailHttpException: 500, Un error ha ocurrido, por favor intente
    mas tarde. (Todas las posibles excepciones no controladas)\n
    Returns:\n
    -   dict -> FilePath
    """
    try:
        now = datetime.datetime.now()
        myquery = {"state": "ACTIVO"}
        newvalues = {
            "$set": {
                "state": "INACTIVO",
                "updated_at": now,
                "updated_by": file_path.created_by,
            }
        }
        await db.paths.update_many(myquery, newvalues)
        file_path.created_at = now
        new_file_path = await db.paths.insert_one(file_path.model_dump())
        path = await db.paths.find_one({"_id": new_file_path.inserted_id})
        path["id"] = str(path["_id"])  # type: ignore
        del path["_id"]  # type: ignore
        return path

    except Exception as exc:        
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR,
        )


@router.get(
    "/status_active",
    status_code=status.HTTP_200_OK,
    response_description="FilePath activo",
    tags=["file_path"],
)
async def file_path_by_state():
    """
    <b>Debe existir un único FilePath activo</b>\n
    Args:\n
    -   N/A \n
    Raises:\n
    -   DetailHttpException, 422, "No existe un path activo"
    -   DetailHttpException: 500, Un error ha ocurrido, por favor
    intente mas tarde. (Todas las posibles excepciones no controladas)\n
    Returns: \n
    -   dict -> FilePath
    """
    try:
        active_file_path = await db.paths.find_one({"state": "ACTIVO"})

        if not active_file_path:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, msg.PATH_NOT_FOUND
            )

        active_file_path["id"] = str(active_file_path["_id"])
        del active_file_path["_id"]
        return active_file_path

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}==>{exc.__cause__}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.put(
    "/{id}",
    status_code=status.HTTP_201_CREATED,
    response_description="Listar path de archivos",
    tags=["file_path"],
)
async def update_file_path(id: str, file_path: UpdateFilePath):
    """
    <b>Actualizar el estado de un FilePath</b>\n
    Args:\n
    -   id (str): Identificador del path
    -   file_path (UpdateFilePath, optional): Modelo a ser actualizado \n
    Raises: \n
    -   DetailHttpException: 422, No exite el path
    -   DetailHttpException: 500, Un error ha ocurrido, por favor
    intente mas tarde. (Todas las posibles excepciones no controladas)\n
    Returns:\n
    -   dict -> FilePath
    """
    try:
        now = datetime.datetime.now()
        file_path.updated_at = now
        my_dict = {}
        for campo, valor in dict(file_path).items():
            if valor is not None:
                my_dict[campo] = valor

        existing_path = await db.paths.find_one({"_id": ObjectId(id)})
        if not existing_path:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, msg.PATH_NOT_FOUND
            )

        update_product = await db.paths.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": my_dict}
        )
        update_product["id"] = str(update_product["_id"])
        del update_product["_id"]
        return update_product

    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_201_CREATED,
    response_description="Listar path de archivos",
    tags=["file_path"],
)
async def delete_file_path(id: str):
    """
    <b>Eliminar un path a partir del _id:</b> \n
    Args:\n
    -   id (str): Identificador del FilePath a se eliminado
    Raises:
    -   DetailHttpException: 500, Un error ha ocurrido, por favor
    intente mas tarde. (Todas las posibles excepciones no controladas)
    Returns: \n
    -   dict -> FilePath
    """
    try:
        delete_file_path = await db.paths.find_one_and_delete({"_id": ObjectId(id)})
        delete_file_path["id"] = str(delete_file_path["_id"])
        del delete_file_path["_id"]
        return delete_file_path

    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )
