"""File management service layer"""

import datetime
import json
import zipfile
from io import BytesIO
from os import makedirs, remove
from typing import Dict, List, Any, Optional

from fastapi import UploadFile, status
from bson import ObjectId

from app.db.database import db
from app.config.settings import settings
from app.config.messages import Messages as msg
from app.utils.exceptions import DetailHttpException
from app.utils.file_validation import validate_file
from app.utils.mongo_utils import (
    transform_mongo_id, transform_mongo_list, find_document_by_id,
    update_document_by_id, delete_document_by_id, paginated_find,
    PaginationParams, build_filter_query
)
from app.utils.validations import validate_field_int, validate_field_str, verificar_documento_firmado
from app.utils.cache import cache_manager, cached_result
from app.schemas.error_content_schema import ErrorContentSchema as Detail


class FileService:
    """Servicio para manejo de archivos"""
    
    def __init__(self):
        self.server_path = settings.SERVER_PATH
    
    async def get_active_file_path(self) -> Dict[str, Any]:
        """
        Obtiene el path activo para guardar archivos.
        
        Returns:
            Dict: Path activo
            
        Raises:
            DetailHttpException: Si no existe path activo
        """
        active_file_path = await db.paths.find_one({"state": "ACTIVO"})
        if not active_file_path:
            raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.PATH_NOT_FOUND)
        return active_file_path
    
    def validate_document_data(self, document_data: Dict[str, Any]) -> None:
        """
        Valida los datos del documento.
        
        Args:
            document_data: Datos del documento a validar
        """
        validate_field_int("file_type_id", document_data["file_type_id"])
        validate_field_str("aplication_id", document_data["aplication_id"])
        validate_field_int("created_by", document_data["created_by"])
        validate_field_int("person_id", document_data["person_id"])
    
    def build_file_path(self, document_data: Dict[str, Any], active_path: str) -> str:
        """
        Construye la ruta donde se guardará el archivo.
        
        Args:
            document_data: Datos del documento
            active_path: Path activo
            
        Returns:
            str: Ruta completa del archivo
        """
        now = datetime.datetime.now()
        return (
            f"{self.server_path}/{active_path}/"
            f'{document_data["aplication_id"]}/{now.strftime("%Y")}/'
            f'{now.strftime("%m")}/{now.strftime("%d")}/'
            f'{document_data["file_type_id"]}/'
        )
    
    async def save_file_to_zip(self, file_path: str, document_id: str, file: UploadFile, content: bytes) -> None:
        """
        Guarda el archivo en un ZIP.
        
        Args:
            file_path: Ruta donde guardar
            document_id: ID del documento
            file: Archivo original
            content: Contenido del archivo
        """
        makedirs(file_path, exist_ok=True)
        
        with zipfile.ZipFile(f"{file_path}{document_id}.zip", "w") as archivo_zip:
            archivo_zip.writestr(
                file.filename,
                content,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    
    async def upload_file(self, file: UploadFile, document: str) -> Dict[str, Any]:
        """
        Sube un archivo al sistema.
        
        Args:
            file: Archivo a subir
            document: Datos del documento en JSON
            
        Returns:
            Dict: Documento creado
        """
        now = datetime.datetime.now()
        document_json = json.loads(document.strip())
        
        # Validar archivo
        sanitized_filename = validate_file(file)
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar datos del documento
        self.validate_document_data(document_json)
        
        # Obtener path activo
        active_file_path = await self.get_active_file_path()
        repo_path_active = active_file_path["path"]
        
        # Construir ruta
        file_path = self.build_file_path(document_json, repo_path_active)
        
        # Preparar datos del documento
        document_json["file_name"] = sanitized_filename
        document_json["file_url"] = file_path
        document_json["active"] = True
        document_json["created_at"] = now
        document_json["block"] = False
        
        # Insertar en base de datos
        new_document_file = await db.files.insert_one(document_json)
        document_get = await db.files.find_one({"_id": new_document_file.inserted_id})
        
        # Guardar archivo físico
        await self.save_file_to_zip(file_path, str(document_get["_id"]), file, file_content)
        
        return transform_mongo_id(document_get)
    
    async def upload_signed_file(self, file: UploadFile, document: str, cedula_ruc: str) -> Dict[str, Any]:
        """
        Sube un archivo firmado digitalmente.
        
        Args:
            file: Archivo a subir
            document: Datos del documento en JSON
            cedula_ruc: Cédula/RUC del firmante
            
        Returns:
            Dict: Documento creado
        """
        now = datetime.datetime.now()
        document_json = json.loads(document.strip())
        
        # Validar archivo
        sanitized_filename = validate_file(file)
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar datos del documento
        self.validate_document_data(document_json)
        
        # Obtener path activo
        active_file_path = await self.get_active_file_path()
        repo_path_active = active_file_path["path"]
        
        # Construir ruta
        file_path = self.build_file_path(document_json, repo_path_active)
        
        # Validar firma digital
        import base64
        documento_base64 = base64.b64encode(file_content)
        result_signed = verificar_documento_firmado(documento_base64)
        
        json_signed = json.loads(result_signed)
        
        if not json_signed["firmasValidas"]:
            raise DetailHttpException(422, msg.VALIDATE_SIGNED)
        
        # Validar firmante
        identity = 0
        for certify in json_signed["certificado"]:
            if (
                certify["cedula"] == cedula_ruc.strip()
                or certify["cedula"] == cedula_ruc.strip()[0:10]
            ):
                identity += 1
        
        if identity == 0:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, 
                msg.VALIDATE_SIGNED_PROVIDER
            )
        
        # Preparar datos del documento
        document_json["file_name"] = sanitized_filename
        document_json["file_url"] = file_path
        document_json["active"] = True
        document_json["created_at"] = now
        document_json["block"] = False
        document_json["signed"] = json_signed
        
        # Insertar en base de datos
        new_document_file = await db.files.insert_one(document_json)
        document_get = await db.files.find_one({"_id": new_document_file.inserted_id})
        
        # Guardar archivo físico
        await self.save_file_to_zip(file_path, str(document_get["_id"]), file, file_content)
        
        # Invalidate cache after new file upload
        await cache_manager.invalidate_file_cache(str(document_get["_id"]))
        
        return transform_mongo_id(document_get)
    
    async def get_documents_by_filters(
        self, 
        person_id: Optional[int] = None,
        aplication_id: Optional[str] = None,
        file_type_ids: Optional[List[int]] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Dict[str, Any]:
        """
        Obtiene documentos filtrados con paginación con cache.
        
        Args:
            person_id: ID de la persona
            aplication_id: ID de la aplicación
            file_type_ids: Lista de tipos de archivo
            pagination: Parámetros de paginación
            
        Returns:
            Dict: Documentos encontrados con paginación
        """
        # Generate cache key
        cache_key = cache_manager.file_list_cache_key({
            "person_id": person_id,
            "aplication_id": aplication_id,
            "file_type_ids": file_type_ids,
            "page": pagination.page if pagination else 1,
            "page_size": pagination.page_size if pagination else 10
        })
        
        # Try to get from cache first
        async def fetch_documents():
            filters = {}
            if person_id:
                filters["person_id"] = person_id
            if aplication_id:
                filters["aplication_id"] = aplication_id
            if file_type_ids:
                filters["file_type_ids"] = file_type_ids
            
            query = build_filter_query(filters)
            
            if pagination:
                return await paginated_find(db.files, query, pagination)
            else:
                # Sin paginación (para mantener compatibilidad)
                documents = await db.files.find(query).to_list()
                if not documents:
                    raise DetailHttpException(status.HTTP_404_NOT_FOUND, msg.RECORD_NOT_FOUND)
                return transform_mongo_list(documents)
        
        # Use cached result with 5 minute TTL for file lists
        from datetime import timedelta
        return await cached_result(cache_key, fetch_documents, timedelta(minutes=5))
    
    async def get_document_by_id(self, document_id: str) -> Dict[str, Any]:
        """
        Obtiene un documento por ID con cache.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Dict: Documento encontrado
        """
        cache_key = cache_manager.file_cache_key(document_id)
        
        async def fetch_document():
            document = await find_document_by_id(db.files, document_id)
            return transform_mongo_id(document)
        
        # Cache individual files for 10 minutes
        from datetime import timedelta
        return await cached_result(cache_key, fetch_document, timedelta(minutes=10))
    
    async def download_document(self, document_id: str) -> tuple[BytesIO, str]:
        """
        Descarga un documento.
        
        Args:
            document_id: ID del documento
            
        Returns:
            tuple: (contenido_archivo, nombre_archivo)
        """
        document = await find_document_by_id(db.files, document_id)
        
        file_path = f'{document["file_url"]}{document_id}.zip'
        file_buffer = BytesIO()
        
        try:
            with zipfile.ZipFile(file_path) as zip_file:
                for name in zip_file.namelist():
                    with zip_file.open(name) as zipped_file:
                        file_buffer.write(zipped_file.read())
            
            file_buffer.seek(0)
            return file_buffer, document["file_name"]
        except Exception as e:
            raise DetailHttpException(
                status.HTTP_404_NOT_FOUND,
                Detail(
                    code="FILE0015",
                    message="No se pudo acceder al archivo físico"
                )
            )
    
    async def update_document(self, document_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un documento.
        
        Args:
            document_id: ID del documento
            document_data: Datos a actualizar
            
        Returns:
            Dict: Documento actualizado
        """
        # Validar campo block si está presente
        if "block" in document_data:
            if document_data["block"] not in [True, False]:
                raise DetailHttpException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    Detail(
                        code=msg.VALIDATION_ERR.code,
                        message=f"{msg.VALIDATION_ERR.message}, el parametro (block) enviado no es correcto",
                    ),
                )
        
        updated_document = await update_document_by_id(db.files, document_id, document_data)
        return transform_mongo_id(updated_document)
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Elimina un documento y su archivo físico.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Dict: Documento eliminado
        """
        document = await find_document_by_id(db.files, document_id)
        
        # Eliminar archivo físico
        try:
            file_path = f'{document["file_url"]}{document_id}.zip'
            remove(file_path)
        except FileNotFoundError:
            pass  # El archivo ya no existe
        except Exception as e:
            # Log del error pero continuar con la eliminación de la BD
            pass
        
        # Eliminar de base de datos
        deleted_document = await delete_document_by_id(db.files, document_id)
        
        # Invalidate cache for this file
        await cache_manager.invalidate_file_cache(document_id)
        
        return transform_mongo_id(deleted_document)