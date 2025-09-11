"""Path management service layer"""

import datetime
from typing import Dict, List, Any, Optional

from app.db.database import db
from app.config.messages import Messages as msg
from app.utils.exceptions import DetailHttpException
from app.utils.mongo_utils import (
    transform_mongo_id, transform_mongo_list, find_document_by_id,
    update_document_by_id, delete_document_by_id, clean_update_dict
)
from app.models.file_path import FilePath, UpdateFilePath
from app.utils.cache import cache_manager, cached_result
from fastapi import status


class PathService:
    """Servicio para manejo de paths de archivos"""
    
    async def get_all_paths(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los paths con cache.
        
        Returns:
            List: Lista de todos los paths
        """
        cache_key = cache_manager.path_cache_key("all")
        
        async def fetch_paths():
            paths = await db.paths.find().to_list()
            return transform_mongo_list(paths)
        
        # Cache paths for 15 minutes since they don't change often
        from datetime import timedelta
        return await cached_result(cache_key, fetch_paths, timedelta(minutes=15))
    
    async def create_path(self, file_path: FilePath) -> Dict[str, Any]:
        """
        Crea un nuevo path y desactiva el anterior activo.
        
        Args:
            file_path: Datos del path a crear
            
        Returns:
            Dict: Path creado
        """
        now = datetime.datetime.now()
        
        # Desactivar paths activos existentes
        await db.paths.update_many(
            {"state": "ACTIVO"},
            {
                "$set": {
                    "state": "INACTIVO",
                    "updated_at": now,
                    "updated_by": file_path.created_by,
                }
            }
        )
        
        # Crear nuevo path
        file_path.created_at = now
        new_file_path = await db.paths.insert_one(file_path.model_dump())
        path = await db.paths.find_one({"_id": new_file_path.inserted_id})
        
        # Clear paths cache after creation
        await cache_manager.invalidate_user_cache("paths")  # Clear all path-related cache
        
        return transform_mongo_id(path)
    
    async def get_active_path(self) -> Dict[str, Any]:
        """
        Obtiene el path activo.
        
        Returns:
            Dict: Path activo
            
        Raises:
            DetailHttpException: Si no existe path activo
        """
        active_file_path = await db.paths.find_one({"state": "ACTIVO"})
        
        if not active_file_path:
            raise DetailHttpException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, 
                msg.PATH_NOT_FOUND
            )
        
        return transform_mongo_id(active_file_path)
    
    async def update_path(self, path_id: str, file_path: UpdateFilePath) -> Dict[str, Any]:
        """
        Actualiza un path.
        
        Args:
            path_id: ID del path
            file_path: Datos a actualizar
            
        Returns:
            Dict: Path actualizado
        """
        now = datetime.datetime.now()
        file_path.updated_at = now
        
        # Limpiar datos nulos
        update_data = clean_update_dict(file_path.model_dump())
        
        updated_path = await update_document_by_id(
            db.paths, 
            path_id, 
            update_data, 
            msg.PATH_NOT_FOUND
        )
        
        return transform_mongo_id(updated_path)
    
    async def delete_path(self, path_id: str) -> Dict[str, Any]:
        """
        Elimina un path.
        
        Args:
            path_id: ID del path
            
        Returns:
            Dict: Path eliminado
        """
        deleted_path = await delete_document_by_id(db.paths, path_id)
        return transform_mongo_id(deleted_path)
    
    async def get_path_by_id(self, path_id: str) -> Dict[str, Any]:
        """
        Obtiene un path por ID.
        
        Args:
            path_id: ID del path
            
        Returns:
            Dict: Path encontrado
        """
        path = await find_document_by_id(db.paths, path_id, msg.PATH_NOT_FOUND)
        return transform_mongo_id(path)