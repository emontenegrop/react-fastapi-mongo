tags_metadata = [
    {
        "name": "document_file",
        "description": "**File Management Operations**\n\n"
                      "Endpoints for uploading, downloading, and managing document files. "
                      "Supports regular file uploads and digitally signed document validation. "
                      "All file operations include security validations and proper error handling."
    },
    {
        "name": "file_path", 
        "description": "**Path Management Operations**\n\n"
                      "Endpoints for managing file storage paths. "
                      "Controls where uploaded files are stored in the filesystem. "
                      "Only one path can be active at a time to ensure consistent file storage."
    },
    {
        "name": "health",
        "description": "**Health Check Operations**\n\n"
                      "System health monitoring endpoints. "
                      "Used to verify that the application and database connections are working properly."
    },
    {
        "name": "auth",
        "description": "**Authentication Operations**\n\n"
                      "JWT-based authentication endpoints including login, logout, "
                      "token refresh, and user profile management."
    }
]
