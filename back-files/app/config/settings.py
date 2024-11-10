from decouple import config


class Settings(object):
   
    MONGO_USER = config("MONGO_USER")
    MONGO_PASSWORD = config("MONGO_PASSWORD")
    MONGO_HOST = config("MONGO_HOST")
    MONGO_PORT = config("MONGO_PORT", cast=int)
    MONGO_DB = config("MONGO_DB")
    LOG_LEVEL = config("LOG_LEVEL")
    CORS_ORIGIN = config("CORS_ORIGIN")
    TIMEOUT = config("TIMEOUT", cast=int)
    SERVER_PATH = config("SERVER_PATH")
    WS_VALIDACION_FIRMA = config("WS_VALIDACION_FIRMA")

    BACK_LOGS = config("BACK_LOGS")


settings = Settings()
