db = db.getSiblingDB('admin');

db.createUser({
  user: "archivos_app",
  pwd: "archivo_secure_2024_Password123",
  roles: [
    { role: "readWrite", db: "archivos" },
    { role: "dbOwner", db: "archivos" },
    { role: "backup", db: "admin" },
    { role: "restore", db: "admin" }
  ]
});

// Switch to the archivos database
db = db.getSiblingDB('archivos');

// Create collections with validation
db.createCollection('files', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["file_name", "file_url", "file_type_id", "aplication_id", "person_id", "created_by", "active"],
      properties: {
        file_name: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        file_url: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        file_type_id: {
          bsonType: "int",
          minimum: 1,
          description: "must be a positive integer and is required"
        },
        aplication_id: {
          bsonType: "string",
          minLength: 1,
          description: "must be a non-empty string and is required"
        },
        person_id: {
          bsonType: "int",
          minimum: 1,
          description: "must be a positive integer and is required"
        },
        created_by: {
          bsonType: "int",
          minimum: 1,
          description: "must be a positive integer and is required"
        },
        active: {
          bsonType: "bool",
          description: "must be a boolean and is required"
        },
        block: {
          bsonType: "bool",
          description: "must be a boolean"
        },
        created_at: {
          bsonType: "date",
          description: "must be a date"
        },
        updated_at: {
          bsonType: "date",
          description: "must be a date"
        }
      }
    }
  }
});

db.createCollection('paths', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["path", "state", "created_by"],
      properties: {
        path: {
          bsonType: "string",
          minLength: 1,
          description: "must be a non-empty string and is required"
        },
        state: {
          bsonType: "string",
          enum: ["ACTIVO", "INACTIVO", "MANTENIMIENTO"],
          description: "must be one of the enum values and is required"
        },
        created_by: {
          bsonType: "int",
          minimum: 1,
          description: "must be a positive integer and is required"
        },
        created_at: {
          bsonType: "date",
          description: "must be a date"
        },
        updated_at: {
          bsonType: "date", 
          description: "must be a date"
        }
      }
    }
  }
});

// Create indexes for optimal performance
db.files.createIndex({ "person_id": 1, "aplication_id": 1 });
db.files.createIndex({ "file_type_id": 1 });
db.files.createIndex({ "created_at": -1 });
db.files.createIndex({ "active": 1 });
db.files.createIndex({ "block": 1 });
db.files.createIndex({ "person_id": 1, "aplication_id": 1, "file_type_id": 1 });

db.paths.createIndex(
  { "state": 1 }, 
  { 
    unique: true, 
    partialFilterExpression: { "state": "ACTIVO" } 
  }
);
db.paths.createIndex({ "created_at": -1 });

// Create health check collection
db.createCollection('health_check');

print('MongoDB initialization completed successfully');