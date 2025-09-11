"""MongoDB utilities and common operations"""

from typing import Dict, List, Any, Optional
from bson import ObjectId
from pymongo.errors import PyMongoError
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.exceptions import DetailHttpException
from app.config.messages import Messages as msg
from fastapi import status


def transform_mongo_id(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma el _id de MongoDB a id para respuestas de API.
    
    Args:
        document: Documento de MongoDB
        
    Returns:
        Dict: Documento con _id transformado a id
    """
    if document and "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return document


def transform_mongo_list(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforma una lista de documentos de MongoDB.
    
    Args:
        documents: Lista de documentos de MongoDB
        
    Returns:
        List: Lista de documentos transformados
    """
    return [transform_mongo_id(doc) for doc in documents]


def validate_object_id(id_str: str) -> ObjectId:
    """
    Valida y convierte un string a ObjectId.
    
    Args:
        id_str: String del ID a validar
        
    Returns:
        ObjectId: ObjectId válido
        
    Raises:
        DetailHttpException: Si el ID no es válido
    """
    try:
        return ObjectId(id_str)
    except Exception:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            msg.RECORD_NOT_FOUND
        )


async def find_document_by_id(
    collection, 
    document_id: str, 
    error_message: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Busca un documento por ID con manejo de errores.
    
    Args:
        collection: Colección de MongoDB
        document_id: ID del documento
        error_message: Mensaje de error personalizado
        
    Returns:
        Dict: Documento encontrado
        
    Raises:
        DetailHttpException: Si no se encuentra el documento
    """
    try:
        object_id = validate_object_id(document_id)
        document = await collection.find_one({"_id": object_id})
        
        if not document:
            raise DetailHttpException(
                status.HTTP_404_NOT_FOUND,
                error_message or msg.RECORD_NOT_FOUND
            )
        
        return document
    except DetailHttpException:
        raise
    except Exception as e:
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR
        )


async def update_document_by_id(
    collection,
    document_id: str,
    update_data: Dict[str, Any],
    error_message: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Actualiza un documento por ID.
    
    Args:
        collection: Colección de MongoDB
        document_id: ID del documento
        update_data: Datos a actualizar
        error_message: Mensaje de error personalizado
        
    Returns:
        Dict: Documento actualizado
    """
    try:
        object_id = validate_object_id(document_id)
        
        # Verificar que el documento existe
        existing_doc = await collection.find_one({"_id": object_id})
        if not existing_doc:
            raise DetailHttpException(
                status.HTTP_404_NOT_FOUND,
                error_message or msg.RECORD_NOT_FOUND
            )
        
        # Actualizar documento
        updated_doc = await collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data},
            return_document=True
        )
        
        return updated_doc
    except DetailHttpException:
        raise
    except Exception as e:
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR
        )


async def delete_document_by_id(
    collection,
    document_id: str,
    error_message: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Elimina un documento por ID.
    
    Args:
        collection: Colección de MongoDB
        document_id: ID del documento
        error_message: Mensaje de error personalizado
        
    Returns:
        Dict: Documento eliminado
    """
    try:
        object_id = validate_object_id(document_id)
        
        deleted_doc = await collection.find_one_and_delete({"_id": object_id})
        
        if not deleted_doc:
            raise DetailHttpException(
                status.HTTP_404_NOT_FOUND,
                error_message or msg.RECORD_NOT_FOUND
            )
        
        return deleted_doc
    except DetailHttpException:
        raise
    except Exception as e:
        raise DetailHttpException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg.API_UNEXPECTED_ERROR
        )


async def create_indexes(db: AsyncIOMotorDatabase):
    """
    Crea índices para mejorar el rendimiento de las consultas.
    
    Args:
        db: Base de datos de MongoDB
    """
    try:
        # Índices para la colección de archivos
        await db.files.create_index([("person_id", 1), ("aplication_id", 1)])
        await db.files.create_index([("file_type_id", 1)])
        await db.files.create_index([("created_at", -1)])
        await db.files.create_index([("active", 1)])
        await db.files.create_index([("block", 1)])
        
        # Índices para la colección de paths
        await db.paths.create_index([("state", 1)], unique=True, partialFilterExpression={"state": "ACTIVO"})
        await db.paths.create_index([("created_at", -1)])
        
        print("Índices de base de datos creados exitosamente")
        
    except PyMongoError as e:
        print(f"Error al crear índices: {e}")
    except Exception as e:
        print(f"Error inesperado al crear índices: {e}")


def build_filter_query(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye una query de filtros para MongoDB.
    
    Args:
        filters: Diccionario con filtros
        
    Returns:
        Dict: Query de MongoDB
    """
    query = {}
    
    for key, value in filters.items():
        if value is not None:
            if key == "file_type_ids" and isinstance(value, list):
                # Para filtros de tipo "in"
                query["file_type_id"] = {"$in": value}
            elif key == "search" and isinstance(value, str):
                # Para búsquedas de texto
                query["$or"] = [
                    {"file_name": {"$regex": value, "$options": "i"}},
                    {"aplication_id": {"$regex": value, "$options": "i"}}
                ]
            elif key == "date_from":
                # Para filtros de fecha
                if "created_at" not in query:
                    query["created_at"] = {}
                query["created_at"]["$gte"] = value
            elif key == "date_to":
                if "created_at" not in query:
                    query["created_at"] = {}
                query["created_at"]["$lte"] = value
            else:
                query[key] = value
    
    return query


class PaginationParams:
    """Parámetros de paginación"""
    
    def __init__(self, skip: int = 0, limit: int = 10, max_limit: int = 100):
        self.skip = max(0, skip)
        self.limit = min(max(1, limit), max_limit)
    
    def get_skip_limit(self):
        return self.skip, self.limit


async def paginated_find(
    collection,
    filter_query: Dict[str, Any],
    pagination: PaginationParams,
    sort_field: str = "created_at",
    sort_direction: int = -1
) -> Dict[str, Any]:
    """
    Realiza una búsqueda paginada.
    
    Args:
        collection: Colección de MongoDB
        filter_query: Query de filtros
        pagination: Parámetros de paginación
        sort_field: Campo para ordenar
        sort_direction: Dirección del ordenamiento (-1 desc, 1 asc)
        
    Returns:
        Dict: Resultado con documentos y metadatos de paginación
    """
    skip, limit = pagination.get_skip_limit()
    
    # Obtener documentos
    cursor = collection.find(filter_query).sort(sort_field, sort_direction).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    
    # Contar total
    total = await collection.count_documents(filter_query)
    
    # Transformar documentos
    transformed_documents = transform_mongo_list(documents)
    
    return {
        "items": transformed_documents,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }


def clean_update_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Limpia un diccionario removiendo valores None para updates.
    
    Args:
        data: Diccionario con datos
        
    Returns:
        Dict: Diccionario limpio
    """
    return {key: value for key, value in data.items() if value is not None}