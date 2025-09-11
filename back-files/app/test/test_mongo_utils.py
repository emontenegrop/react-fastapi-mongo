"""Tests for MongoDB utilities"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from bson import ObjectId

from app.utils.mongo_utils import (
    transform_mongo_id, transform_mongo_list, validate_object_id,
    find_document_by_id, update_document_by_id, delete_document_by_id,
    build_filter_query, PaginationParams, paginated_find, clean_update_dict
)
from app.utils.exceptions import DetailHttpException
from app.config.messages import Messages as msg


class TestMongoUtils:
    """Test cases for MongoDB utilities"""
    
    def test_transform_mongo_id_with_id(self):
        """Test transforming document with _id field"""
        document = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "test",
            "value": 123
        }
        
        result = transform_mongo_id(document)
        
        assert "id" in result
        assert "_id" not in result
        assert result["id"] == "507f1f77bcf86cd799439011"
        assert result["name"] == "test"
        assert result["value"] == 123
    
    def test_transform_mongo_id_without_id(self):
        """Test transforming document without _id field"""
        document = {
            "name": "test",
            "value": 123
        }
        
        result = transform_mongo_id(document)
        
        assert result == document
        assert "_id" not in result
    
    def test_transform_mongo_id_none(self):
        """Test transforming None document"""
        result = transform_mongo_id(None)
        assert result is None
    
    def test_transform_mongo_list(self):
        """Test transforming list of MongoDB documents"""
        documents = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "doc1"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "doc2"}
        ]
        
        result = transform_mongo_list(documents)
        
        assert len(result) == 2
        assert all("id" in doc for doc in result)
        assert all("_id" not in doc for doc in result)
        assert result[0]["id"] == "507f1f77bcf86cd799439011"
        assert result[1]["id"] == "507f1f77bcf86cd799439012"
    
    def test_validate_object_id_valid(self):
        """Test validating valid ObjectId string"""
        valid_id = "507f1f77bcf86cd799439011"
        result = validate_object_id(valid_id)
        
        assert isinstance(result, ObjectId)
        assert str(result) == valid_id
    
    def test_validate_object_id_invalid(self):
        """Test validating invalid ObjectId string"""
        invalid_ids = ["invalid", "123", "", "xyz123"]
        
        for invalid_id in invalid_ids:
            with pytest.raises(DetailHttpException) as exc_info:
                validate_object_id(invalid_id)
            assert exc_info.value.status_code == 422
    
    @pytest.mark.asyncio
    async def test_find_document_by_id_success(self):
        """Test successful document finding by ID"""
        mock_collection = AsyncMock()
        document_id = "507f1f77bcf86cd799439011"
        expected_doc = {"_id": ObjectId(document_id), "name": "test"}
        
        mock_collection.find_one.return_value = expected_doc
        
        result = await find_document_by_id(mock_collection, document_id)
        
        assert result == expected_doc
        mock_collection.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_document_by_id_not_found(self):
        """Test document finding when document doesn't exist"""
        mock_collection = AsyncMock()
        document_id = "507f1f77bcf86cd799439011"
        
        mock_collection.find_one.return_value = None
        
        with pytest.raises(DetailHttpException) as exc_info:
            await find_document_by_id(mock_collection, document_id)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_document_by_id_success(self):
        """Test successful document update by ID"""
        mock_collection = AsyncMock()
        document_id = "507f1f77bcf86cd799439011"
        update_data = {"name": "updated"}
        existing_doc = {"_id": ObjectId(document_id), "name": "original"}
        updated_doc = {"_id": ObjectId(document_id), "name": "updated"}
        
        mock_collection.find_one.return_value = existing_doc
        mock_collection.find_one_and_update.return_value = updated_doc
        
        result = await update_document_by_id(mock_collection, document_id, update_data)
        
        assert result == updated_doc
        mock_collection.find_one_and_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_document_by_id_not_found(self):
        """Test document update when document doesn't exist"""
        mock_collection = AsyncMock()
        document_id = "507f1f77bcf86cd799439011"
        update_data = {"name": "updated"}
        
        mock_collection.find_one.return_value = None
        
        with pytest.raises(DetailHttpException) as exc_info:
            await update_document_by_id(mock_collection, document_id, update_data)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_document_by_id_success(self):
        """Test successful document deletion by ID"""
        mock_collection = AsyncMock()
        document_id = "507f1f77bcf86cd799439011"
        deleted_doc = {"_id": ObjectId(document_id), "name": "deleted"}
        
        mock_collection.find_one_and_delete.return_value = deleted_doc
        
        result = await delete_document_by_id(mock_collection, document_id)
        
        assert result == deleted_doc
        mock_collection.find_one_and_delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_document_by_id_not_found(self):
        """Test document deletion when document doesn't exist"""
        mock_collection = AsyncMock()
        document_id = "507f1f77bcf86cd799439011"
        
        mock_collection.find_one_and_delete.return_value = None
        
        with pytest.raises(DetailHttpException) as exc_info:
            await delete_document_by_id(mock_collection, document_id)
        
        assert exc_info.value.status_code == 404
    
    def test_build_filter_query_simple(self):
        """Test building simple filter query"""
        filters = {
            "name": "test",
            "status": "active",
            "count": 5
        }
        
        result = build_filter_query(filters)
        
        assert result == {
            "name": "test",
            "status": "active", 
            "count": 5
        }
    
    def test_build_filter_query_file_type_ids(self):
        """Test building filter query with file_type_ids"""
        filters = {
            "file_type_ids": [1, 2, 3],
            "name": "test"
        }
        
        result = build_filter_query(filters)
        
        assert result == {
            "file_type_id": {"$in": [1, 2, 3]},
            "name": "test"
        }
    
    def test_build_filter_query_search(self):
        """Test building filter query with search term"""
        filters = {
            "search": "test query",
            "status": "active"
        }
        
        result = build_filter_query(filters)
        
        assert "$or" in result
        assert result["status"] == "active"
        assert len(result["$or"]) == 2
    
    def test_build_filter_query_date_range(self):
        """Test building filter query with date range"""
        from datetime import datetime
        date_from = datetime(2024, 1, 1)
        date_to = datetime(2024, 12, 31)
        
        filters = {
            "date_from": date_from,
            "date_to": date_to,
            "status": "active"
        }
        
        result = build_filter_query(filters)
        
        assert "created_at" in result
        assert result["created_at"]["$gte"] == date_from
        assert result["created_at"]["$lte"] == date_to
        assert result["status"] == "active"
    
    def test_build_filter_query_none_values(self):
        """Test building filter query ignoring None values"""
        filters = {
            "name": "test",
            "status": None,
            "count": 0
        }
        
        result = build_filter_query(filters)
        
        assert result == {
            "name": "test",
            "count": 0
        }
        assert "status" not in result
    
    def test_pagination_params_default(self):
        """Test PaginationParams with default values"""
        pagination = PaginationParams()
        skip, limit = pagination.get_skip_limit()
        
        assert skip == 0
        assert limit == 10
    
    def test_pagination_params_custom(self):
        """Test PaginationParams with custom values"""
        pagination = PaginationParams(skip=20, limit=50)
        skip, limit = pagination.get_skip_limit()
        
        assert skip == 20
        assert limit == 50
    
    def test_pagination_params_limits(self):
        """Test PaginationParams enforces limits"""
        # Test negative skip
        pagination = PaginationParams(skip=-5, limit=5)
        skip, limit = pagination.get_skip_limit()
        assert skip == 0
        
        # Test zero limit
        pagination = PaginationParams(skip=0, limit=0)
        skip, limit = pagination.get_skip_limit()
        assert limit == 1
        
        # Test excessive limit
        pagination = PaginationParams(skip=0, limit=200, max_limit=100)
        skip, limit = pagination.get_skip_limit()
        assert limit == 100
    
    @pytest.mark.asyncio
    async def test_paginated_find_success(self):
        """Test successful paginated find operation"""
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        
        # Mock documents
        documents = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "doc1"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "doc2"}
        ]
        
        mock_cursor.to_list.return_value = documents
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
        mock_collection.count_documents.return_value = 25
        
        filter_query = {"status": "active"}
        pagination = PaginationParams(skip=0, limit=10)
        
        with patch('app.utils.mongo_utils.transform_mongo_list') as mock_transform:
            mock_transform.return_value = [
                {"id": "507f1f77bcf86cd799439011", "name": "doc1"},
                {"id": "507f1f77bcf86cd799439012", "name": "doc2"}
            ]
            
            result = await paginated_find(mock_collection, filter_query, pagination)
            
            assert "items" in result
            assert "pagination" in result
            assert len(result["items"]) == 2
            assert result["pagination"]["total"] == 25
            assert result["pagination"]["has_next"] == True
            assert result["pagination"]["has_prev"] == False
    
    def test_clean_update_dict(self):
        """Test cleaning update dictionary by removing None values"""
        data = {
            "name": "test",
            "status": None,
            "count": 0,
            "description": "updated",
            "tags": None
        }
        
        result = clean_update_dict(data)
        
        expected = {
            "name": "test",
            "count": 0,
            "description": "updated"
        }
        
        assert result == expected
        assert "status" not in result
        assert "tags" not in result