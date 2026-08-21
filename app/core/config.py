from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str="localhost"
    DB_PORT: int=3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    JWT_SECRET: str
    SERVER_PORT: int=8080
    class Config:
        env_file = ".env"

settings = Settings()