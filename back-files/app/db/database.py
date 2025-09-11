from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

# Create MongoDB client with connection pooling
client = AsyncIOMotorClient(
    settings.mongo_url,
    maxPoolSize=settings.CONNECTION_POOL_SIZE,
    minPoolSize=1,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=settings.REQUEST_TIMEOUT * 1000,
    retryWrites=True,
    retryReads=True
)

db = client[settings.MONGO_DB]
