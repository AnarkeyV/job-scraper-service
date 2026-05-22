from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Job Scraper Service"
    public_base_url: str = "http://localhost:8000"
    database_path: str = "data/jobs.db"
    max_scans_per_day: int = 3
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
