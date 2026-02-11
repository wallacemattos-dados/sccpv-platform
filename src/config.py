from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "SCCPV - Sistema FIPE"
    DATABASE_URL: str = "sqlite:///./sccpv.db"
    SECRET_KEY: str = "segredo_padrao_trocar_em_prod"
    
    # Permite ler do arquivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()