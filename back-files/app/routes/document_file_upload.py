import traceback
from typing import Optional, List

from app.config.messages import Messages as msg
from app.logger import logger
from app.middleware.router_error_handler import RouteErrorHandler
from app.schemas.error_content_schema import ErrorContentSchema as Detail
from app.utils.exceptions import DetailHttpException
from app.utils.mongo_utils import PaginationParams
from app.services.file_service import FileService
from fastapi import APIRouter, File, Form, UploadFile, status, Query
from fastapi.responses import StreamingResponse

router = APIRouter(route_class=RouteErrorHandler)
file_service = FileService()


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_description="Crear un nuevo documento y cargar el archivo",
    tags=["document_file"],
)
async def file_upload(file: UploadFile = File(...), document: str = Form()):
    """
    Upload a new document file.
    
    Args:
        file: The file to upload
        document: JSON string with document metadata containing:
            - file_type_id (int): File type identifier
            - aplication_id (str): Application identifier
            - created_by (int): User ID who created the document
            - person_id (int): Person ID associated with the document
            
    Returns:
        dict: Created document with generated ID and metadata
        
    Raises:
        DetailHttpException: 404 if no active path found
        DetailHttpException: 422 if validation fails
        DetailHttpException: 413 if file size exceeds limit
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await file_service.upload_file(file, document)
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
    response_description="Listar todos los documentos de la persona con paginación",
    tags=["document_file"],
)
async def get_documents_by_type(
    person_id: int,
    aplication_id: str,
    file_type_id: str,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver")
):
    """
    List files filtered by person, application, and file type with pagination.
    
    Args:
        person_id: Person identifier
        aplication_id: Application identifier
        file_type_id: File type identifier (comma-separated list of numbers)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-100)
        
    Returns:
        dict: Paginated list of files with metadata
        
    Raises:
        DetailHttpException: 404 if no records found
        DetailHttpException: 422 if validation fails
        DetailHttpException: 500 for unexpected errors
    """
    try:
        # Parsear tipos de archivo
        types_in = []
        type_list = file_type_id.split(",")
        for type_file in type_list:
            types_in.append(int(type_file.strip()))
        
        pagination = PaginationParams(skip=skip, limit=limit)
        
        result = await file_service.get_documents_by_filters(
            person_id=person_id,
            aplication_id=aplication_id,
            file_type_ids=types_in,
            pagination=pagination
        )
        
        return result

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
    Download a document file.
    
    Args:
        id: Document identifier
        
    Returns:
        StreamingResponse: File content as downloadable attachment
        
    Raises:
        DetailHttpException: 404 if document not found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        file_buffer, filename = await file_service.download_document(id)
        
        return StreamingResponse(
            file_buffer,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
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
    Get document data by ID.
    
    Args:
        id: Document identifier
        
    Returns:
        dict: Document data
        
    Raises:
        DetailHttpException: 404 if document not found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await file_service.get_document_by_id(id)
    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
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
    Update document state (block status).
    
    Args:
        id: Document identifier
        document: Update data containing:
            - block (bool): Whether the file is deletable (False) or not (True)
            
    Returns:
        dict: Updated document
        
    Raises:
        DetailHttpException: 422 if validation fails
        DetailHttpException: 404 if document not found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await file_service.update_document(id, document)
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
async def document_delete(id: str):
    """
    Delete document and its physical file.
    
    Args:
        id: Document identifier
        
    Returns:
        dict: Deleted document data
        
    Raises:
        DetailHttpException: 404 if document not found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await file_service.delete_document(id)
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
    response_description="Listar todos los documentos de la persona con paginación",
    tags=["document_file"],
)
async def get_documents(
    person_id: int,
    aplication_id: str,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver")
):
    """
    List files filtered by person and application with pagination.
    
    Args:
        person_id: Person identifier
        aplication_id: Application identifier
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-100)
        
    Returns:
        dict: Paginated list of files with metadata
        
    Raises:
        DetailHttpException: 404 if no records found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        
        result = await file_service.get_documents_by_filters(
            person_id=person_id,
            aplication_id=aplication_id,
            pagination=pagination
        )
        
        return result

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
    file: UploadFile = File(...), 
    document: str = Form(), 
    cedula_ruc: str = Form()
):
    """
    Upload a new digitally signed document with validation.
    
    Args:
        file: The signed file to upload
        document: JSON string with document metadata
        cedula_ruc: ID card or RUC number of the signer
        
    Returns:
        dict: Created document with signature validation results
        
    Raises:
        DetailHttpException: 422 if signature validation fails
        DetailHttpException: 404 if no active path found
        DetailHttpException: 500 for unexpected errors
    """
    try:
        return await file_service.upload_signed_file(file, document, cedula_ruc)
    except DetailHttpException as dexc:
        logger.debug(f"{traceback.format_exc()}")
        raise dexc
    except Exception as exc:
        logger.debug(f"{traceback.format_exc()}")
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, msg.API_UNEXPECTED_ERROR
        )