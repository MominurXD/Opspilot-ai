from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "OpsPilot AI"
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
