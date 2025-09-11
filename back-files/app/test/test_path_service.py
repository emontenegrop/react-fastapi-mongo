"""Tests for path service layer"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.services.path_service import PathService
from app.models.file_path import FilePath, UpdateFilePath
from app.utils.exceptions import DetailHttpException
from app.config.messages import Messages as msg


class TestPathService:
    """Test cases for PathService"""
    
    @pytest.fixture
    def path_service(self):
        """Create PathService instance for testing"""
        return PathService()
    
    @pytest.fixture
    def mock_file_path(self):
        """Create mock FilePath for testing"""
        return FilePath(
            path="/test/path",
            state="ACTIVO",
            created_by=123
        )
    
    @pytest.fixture
    def mock_update_file_path(self):
        """Create mock UpdateFilePath for testing"""
        return UpdateFilePath(
            state="INACTIVO",
            updated_by=456
        )
    
    @pytest.mark.asyncio
    async def test_get_all_paths_success(self, path_service):
        """Test successful retrieval of all paths"""
        mock_paths = [
            {"_id": "507f1f77bcf86cd799439011", "path": "/path1", "state": "ACTIVO"},
            {"_id": "507f1f77bcf86cd799439012", "path": "/path2", "state": "INACTIVO"}
        ]
        
        with patch('app.services.path_service.db.paths.find') as mock_find:
            mock_find.return_value.to_list.return_value = mock_paths
            with patch('app.services.path_service.transform_mongo_list') as mock_transform:
                mock_transform.return_value = [
                    {"id": "507f1f77bcf86cd799439011", "path": "/path1", "state": "ACTIVO"},
                    {"id": "507f1f77bcf86cd799439012", "path": "/path2", "state": "INACTIVO"}
                ]
                
                result = await path_service.get_all_paths()
                
                assert len(result) == 2
                assert result[0]["id"] == "507f1f77bcf86cd799439011"
                mock_transform.assert_called_once_with(mock_paths)
    
    @pytest.mark.asyncio
    async def test_create_path_success(self, path_service, mock_file_path):
        """Test successful path creation"""
        inserted_id = "507f1f77bcf86cd799439011"
        mock_created_path = {
            "_id": inserted_id,
            "path": "/test/path",
            "state": "ACTIVO",
            "created_by": 123
        }
        
        with patch('app.services.path_service.db.paths.update_many') as mock_update_many, \
             patch('app.services.path_service.db.paths.insert_one') as mock_insert, \
             patch('app.services.path_service.db.paths.find_one', return_value=mock_created_path), \
             patch('app.services.path_service.transform_mongo_id') as mock_transform, \
             patch('datetime.datetime') as mock_datetime:
            
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_insert.return_value.inserted_id = inserted_id
            mock_transform.return_value = {
                "id": inserted_id,
                "path": "/test/path",
                "state": "ACTIVO",
                "created_by": 123
            }
            
            result = await path_service.create_path(mock_file_path)
            
            # Verify previous active paths were deactivated
            mock_update_many.assert_called_once_with(
                {"state": "ACTIVO"},
                {
                    "$set": {
                        "state": "INACTIVO",
                        "updated_at": mock_now,
                        "updated_by": 123,
                    }
                }
            )
            
            # Verify new path was created
            mock_insert.assert_called_once()
            assert result["id"] == inserted_id
    
    @pytest.mark.asyncio
    async def test_get_active_path_success(self, path_service):
        """Test successful retrieval of active path"""
        mock_active_path = {
            "_id": "507f1f77bcf86cd799439011",
            "path": "/active/path",
            "state": "ACTIVO"
        }
        
        with patch('app.services.path_service.db.paths.find_one', return_value=mock_active_path), \
             patch('app.services.path_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {
                "id": "507f1f77bcf86cd799439011",
                "path": "/active/path", 
                "state": "ACTIVO"
            }
            
            result = await path_service.get_active_path()
            
            assert result["id"] == "507f1f77bcf86cd799439011"
            assert result["state"] == "ACTIVO"
    
    @pytest.mark.asyncio
    async def test_get_active_path_not_found(self, path_service):
        """Test error when no active path exists"""
        with patch('app.services.path_service.db.paths.find_one', return_value=None):
            with pytest.raises(DetailHttpException) as exc_info:
                await path_service.get_active_path()
            
            assert exc_info.value.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_path_success(self, path_service, mock_update_file_path):
        """Test successful path update"""
        path_id = "507f1f77bcf86cd799439011"
        mock_updated_path = {
            "_id": path_id,
            "path": "/test/path",
            "state": "INACTIVO",
            "updated_by": 456
        }
        
        with patch('app.services.path_service.clean_update_dict') as mock_clean, \
             patch('app.services.path_service.update_document_by_id', return_value=mock_updated_path), \
             patch('app.services.path_service.transform_mongo_id') as mock_transform, \
             patch('datetime.datetime') as mock_datetime:
            
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_clean.return_value = {"state": "INACTIVO", "updated_by": 456, "updated_at": mock_now}
            mock_transform.return_value = {
                "id": path_id,
                "path": "/test/path",
                "state": "INACTIVO",
                "updated_by": 456
            }
            
            result = await path_service.update_path(path_id, mock_update_file_path)
            
            assert result["id"] == path_id
            assert result["state"] == "INACTIVO"
            assert mock_update_file_path.updated_at == mock_now
    
    @pytest.mark.asyncio
    async def test_delete_path_success(self, path_service):
        """Test successful path deletion"""
        path_id = "507f1f77bcf86cd799439011"
        mock_deleted_path = {
            "_id": path_id,
            "path": "/test/path",
            "state": "INACTIVO"
        }
        
        with patch('app.services.path_service.delete_document_by_id', return_value=mock_deleted_path), \
             patch('app.services.path_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {
                "id": path_id,
                "path": "/test/path",
                "state": "INACTIVO"
            }
            
            result = await path_service.delete_path(path_id)
            
            assert result["id"] == path_id
    
    @pytest.mark.asyncio
    async def test_get_path_by_id_success(self, path_service):
        """Test successful path retrieval by ID"""
        path_id = "507f1f77bcf86cd799439011"
        mock_path = {
            "_id": path_id,
            "path": "/test/path",
            "state": "ACTIVO"
        }
        
        with patch('app.services.path_service.find_document_by_id', return_value=mock_path), \
             patch('app.services.path_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {
                "id": path_id,
                "path": "/test/path",
                "state": "ACTIVO"
            }
            
            result = await path_service.get_path_by_id(path_id)
            
            assert result["id"] == path_id
            assert result["state"] == "ACTIVO"
    
    @pytest.mark.asyncio
    async def test_get_path_by_id_not_found(self, path_service):
        """Test error when path not found by ID"""
        path_id = "507f1f77bcf86cd799439011"
        
        with patch('app.services.path_service.find_document_by_id', side_effect=DetailHttpException(404, msg.PATH_NOT_FOUND)):
            with pytest.raises(DetailHttpException) as exc_info:
                await path_service.get_path_by_id(path_id)
            
            assert exc_info.value.status_code == 404