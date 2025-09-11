import traceback

from app.config.messages import Messages as msg
from app.logger import logger
from app.middleware.router_error_handler import RouteErrorHandler
from app.models.file_path import FilePath, UpdateFilePath
from app.utils.exceptions import DetailHttpException
from app.services.path_service import PathService
from fastapi import APIRouter, Request, status

router = APIRouter(route_class=RouteErrorHandler)
path_service = PathService()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_description="Listar path de archivos",
    tags=["file_path"],
)
async def get_file_paths():
    """
    List all file paths in the database.
    
    Returns:
        List[dict]: List of all file paths
        
    Raises:
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await path_service.get_all_paths()
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
    response_description="Crear un nuevo path de archivos",
    tags=["file_path"],
)
async def create_file_path(file_path: FilePath):
    """
    Create a new file path and deactivate the previous active one.
    
    Args:
        file_path: FilePath model to be created
        
    Returns:
        dict: Created FilePath
        
    Raises:
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await path_service.create_path(file_path)
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
async def get_active_file_path():
    """
    Get the active file path. There should be only one active path.
    
    Returns:
        dict: Active FilePath
        
    Raises:
        DetailHttpException: 422 if no active path exists
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await path_service.get_active_path()
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
    status_code=status.HTTP_200_OK,
    response_description="Actualizar path de archivos",
    tags=["file_path"],
)
async def update_file_path(id: str, file_path: UpdateFilePath):
    """
    Update a file path.
    
    Args:
        id: Path identifier
        file_path: UpdateFilePath model with data to be updated
        
    Returns:
        dict: Updated FilePath
        
    Raises:
        DetailHttpException: 422 if path not found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await path_service.update_path(id, file_path)
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
    status_code=status.HTTP_200_OK,
    response_description="Eliminar path de archivos",
    tags=["file_path"],
)
async def delete_file_path(id: str):
    """
    Delete a file path by ID.
    
    Args:
        id: FilePath identifier to be deleted
        
    Returns:
        dict: Deleted FilePath
        
    Raises:
        DetailHttpException: 404 if path not found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await path_service.delete_path(id)
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )
