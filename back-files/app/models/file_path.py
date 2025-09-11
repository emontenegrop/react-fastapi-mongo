from datetime import datetime
from typing import Optional
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ConfigDict


class PathState(str, Enum):
    """Valid states for file paths"""
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"
    MAINTENANCE = "MANTENIMIENTO"


class FilePath(BaseModel):
    """Model for file storage paths with enhanced validation"""
    
    path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="File storage path - must be valid and safe"
    )
    state: PathState = Field(
        default=PathState.ACTIVE,
        description="Path state"
    )
    created_by: int = Field(
        ...,
        gt=0,
        description="User ID who created the path"
    )
    updated_by: Optional[int] = Field(
        None,
        gt=0,
        description="User ID who last updated the path"
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "path": "/storage/files/2024",
                "state": "ACTIVO",
                "created_by": 1
            }
        }
    )
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that the path is safe and valid"""
        if not v or not v.strip():
            raise ValueError('Path cannot be empty')
        
        v = v.strip()
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '~/', '///', '<', '>', '|', '?', '*', '"']
        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(f'Path contains unsafe pattern: {pattern}')
        
        # Ensure it's a relative path or starts with allowed absolute paths
        if v.startswith('/'):
            # Allow specific absolute path prefixes
            allowed_prefixes = ['/storage/', '/data/', '/files/', '/uploads/', '/code/repo/']
            if not any(v.startswith(prefix) for prefix in allowed_prefixes):
                raise ValueError('Absolute paths must start with allowed prefixes: /storage/, /data/, /files/, /uploads/, /code/repo/')
        
        # Validate path structure
        try:
            path_obj = Path(v)
            # Check for invalid characters in path parts
            for part in path_obj.parts:
                if not part or part in ['.', '..'] or any(char in part for char in '<>:"|?*'):
                    raise ValueError(f'Invalid path component: {part}')
        except Exception as e:
            raise ValueError(f'Invalid path structure: {e}')
        
        return v
    
    @field_validator('updated_at', mode='before')
    @classmethod
    def validate_updated_at(cls, v, info):
        """Ensure updated_at is after created_at when both are present"""
        if v is not None and info.data.get('created_at') is not None:
            created_at = info.data['created_at']
            if isinstance(created_at, datetime) and isinstance(v, datetime):
                if v < created_at:
                    raise ValueError('updated_at must be after created_at')
        return v


class UpdateFilePath(BaseModel):
    """Model for updating file paths with enhanced validation"""
    
    path: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Updated file storage path"
    )
    state: Optional[PathState] = Field(
        None,
        description="Updated path state"
    )
    updated_by: Optional[int] = Field(
        None,
        gt=0,
        description="User ID who is updating the path"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Update timestamp"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "state": "INACTIVO",
                "updated_by": 2
            }
        }
    )
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate path if provided"""
        if v is None:
            return v
        # Use the same validation as FilePath
        return FilePath.validate_path(v)


class FilePathResponse(BaseModel):
    """Response model for file path operations"""
    
    id: str = Field(..., description="Path ID")
    path: str = Field(..., description="File storage path")
    state: PathState = Field(..., description="Path state")
    created_by: int = Field(..., description="Creator user ID")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )
