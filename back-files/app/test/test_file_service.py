"""Tests for file service layer"""

import pytest
import json
import zipfile
from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch
from fastapi import UploadFile

from app.services.file_service import FileService
from app.utils.exceptions import DetailHttpException
from app.config.messages import Messages as msg


class TestFileService:
    """Test cases for FileService"""
    
    @pytest.fixture
    def file_service(self):
        """Create FileService instance for testing"""
        return FileService()
    
    @pytest.fixture
    def mock_upload_file(self):
        """Create mock UploadFile for testing"""
        file_content = b"test file content"
        file = UploadFile(
            filename="test.pdf",
            file=BytesIO(file_content),
            content_type="application/pdf"
        )
        return file
    
    @pytest.fixture
    def mock_document_data(self):
        """Create mock document data for testing"""
        return {
            "file_type_id": 1,
            "aplication_id": "TEST_APP",
            "created_by": 123,
            "person_id": 456
        }
    
    @pytest.mark.asyncio
    async def test_get_active_file_path_success(self, file_service):
        """Test successful retrieval of active file path"""
        expected_path = {
            "_id": "507f1f77bcf86cd799439011",
            "path": "test/path",
            "state": "ACTIVO"
        }
        
        with patch('app.services.file_service.db.paths.find_one', return_value=expected_path):
            result = await file_service.get_active_file_path()
            assert result == expected_path
    
    @pytest.mark.asyncio
    async def test_get_active_file_path_not_found(self, file_service):
        """Test error when no active file path exists"""
        with patch('app.services.file_service.db.paths.find_one', return_value=None):
            with pytest.raises(DetailHttpException) as exc_info:
                await file_service.get_active_file_path()
            
            assert exc_info.value.status_code == 404
    
    def test_validate_document_data_success(self, file_service, mock_document_data):
        """Test successful document data validation"""
        # Should not raise any exception
        file_service.validate_document_data(mock_document_data)
    
    def test_validate_document_data_invalid_file_type(self, file_service):
        """Test validation failure for invalid file_type_id"""
        invalid_data = {
            "file_type_id": "invalid",
            "aplication_id": "TEST_APP",
            "created_by": 123,
            "person_id": 456
        }
        
        with pytest.raises(DetailHttpException):
            file_service.validate_document_data(invalid_data)
    
    def test_build_file_path(self, file_service, mock_document_data):
        """Test file path building"""
        active_path = "uploads"
        
        with patch('datetime.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.side_effect = lambda fmt: {
                "%Y": "2024",
                "%m": "01", 
                "%d": "15"
            }[fmt]
            mock_datetime.now.return_value = mock_now
            
            result = file_service.build_file_path(mock_document_data, active_path)
            expected = f"{file_service.server_path}/uploads/TEST_APP/2024/01/15/1/"
            assert result == expected
    
    @pytest.mark.asyncio
    async def test_save_file_to_zip(self, file_service, mock_upload_file):
        """Test saving file to ZIP"""
        file_path = "/tmp/test/"
        document_id = "test123"
        content = b"test content"
        
        with patch('app.services.file_service.makedirs') as mock_makedirs, \
             patch('app.services.file_service.zipfile.ZipFile') as mock_zipfile:
            
            mock_zip = Mock()
            mock_zipfile.return_value.__enter__.return_value = mock_zip
            
            await file_service.save_file_to_zip(file_path, document_id, mock_upload_file, content)
            
            mock_makedirs.assert_called_once_with(file_path, exist_ok=True)
            mock_zip.writestr.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_upload_file_success(self, file_service, mock_upload_file, mock_document_data):
        """Test successful file upload"""
        mock_active_path = {"path": "uploads"}
        mock_inserted_id = "507f1f77bcf86cd799439011" 
        mock_document = {
            "_id": mock_inserted_id,
            "file_name": "test.pdf",
            **mock_document_data
        }
        
        with patch('app.services.file_service.validate_file', return_value="test.pdf"), \
             patch.object(file_service, 'get_active_file_path', return_value=mock_active_path), \
             patch.object(file_service, 'validate_document_data'), \
             patch.object(file_service, 'build_file_path', return_value="/tmp/test/"), \
             patch.object(file_service, 'save_file_to_zip'), \
             patch('app.services.file_service.db.files.insert_one') as mock_insert, \
             patch('app.services.file_service.db.files.find_one', return_value=mock_document):
            
            mock_insert.return_value.inserted_id = mock_inserted_id
            
            result = await file_service.upload_file(mock_upload_file, json.dumps(mock_document_data))
            
            assert result["id"] == mock_inserted_id
            assert "file_name" in result
            assert "_id" not in result
    
    @pytest.mark.asyncio
    async def test_get_document_by_id_success(self, file_service):
        """Test successful document retrieval by ID"""
        document_id = "507f1f77bcf86cd799439011"
        mock_document = {
            "_id": document_id,
            "file_name": "test.pdf"
        }
        
        with patch('app.services.file_service.find_document_by_id', return_value=mock_document), \
             patch('app.services.file_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {"id": document_id, "file_name": "test.pdf"}
            
            result = await file_service.get_document_by_id(document_id)
            
            mock_transform.assert_called_once_with(mock_document)
            assert result["id"] == document_id
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, file_service):
        """Test successful document deletion"""
        document_id = "507f1f77bcf86cd799439011"
        mock_document = {
            "_id": document_id,
            "file_url": "/tmp/test/",
            "file_name": "test.pdf"
        }
        
        with patch('app.services.file_service.find_document_by_id', return_value=mock_document), \
             patch('app.services.file_service.remove') as mock_remove, \
             patch('app.services.file_service.delete_document_by_id', return_value=mock_document), \
             patch('app.services.file_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {"id": document_id, "file_name": "test.pdf"}
            
            result = await file_service.delete_document(document_id)
            
            mock_remove.assert_called_once_with(f"/tmp/test/{document_id}.zip")
            assert result["id"] == document_id
    
    @pytest.mark.asyncio
    async def test_delete_document_file_not_found(self, file_service):
        """Test document deletion when physical file doesn't exist"""
        document_id = "507f1f77bcf86cd799439011"
        mock_document = {
            "_id": document_id,
            "file_url": "/tmp/test/",
            "file_name": "test.pdf"
        }
        
        with patch('app.services.file_service.find_document_by_id', return_value=mock_document), \
             patch('app.services.file_service.remove', side_effect=FileNotFoundError), \
             patch('app.services.file_service.delete_document_by_id', return_value=mock_document), \
             patch('app.services.file_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {"id": document_id, "file_name": "test.pdf"}
            
            # Should not raise exception even if file doesn't exist
            result = await file_service.delete_document(document_id)
            assert result["id"] == document_id
    
    @pytest.mark.asyncio
    async def test_update_document_success(self, file_service):
        """Test successful document update"""
        document_id = "507f1f77bcf86cd799439011"
        update_data = {"block": True}
        mock_updated_doc = {
            "_id": document_id,
            "block": True,
            "file_name": "test.pdf"
        }
        
        with patch('app.services.file_service.update_document_by_id', return_value=mock_updated_doc), \
             patch('app.services.file_service.transform_mongo_id') as mock_transform:
            
            mock_transform.return_value = {"id": document_id, "block": True, "file_name": "test.pdf"}
            
            result = await file_service.update_document(document_id, update_data)
            
            assert result["id"] == document_id
            assert result["block"] == True
    
    @pytest.mark.asyncio
    async def test_update_document_invalid_block(self, file_service):
        """Test document update with invalid block value"""
        document_id = "507f1f77bcf86cd799439011"
        invalid_data = {"block": "invalid"}
        
        with pytest.raises(DetailHttpException) as exc_info:
            await file_service.update_document(document_id, invalid_data)
        
        assert exc_info.value.status_code == 422