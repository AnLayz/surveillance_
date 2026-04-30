from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str

    # CV settings
    yolo_model_path: str = "models_weights/yolov8n.pt"
    camera_source: str | int = 0       # 0 = webcam, or path to video file
    confidence_threshold: float = 0.5

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Incident Management System integration
    ims_url: str = ""
    ims_username: str = ""
    ims_password: str = ""

    # App
    app_name: str = "Survivalence"
    debug: bool = False


# Single shared instance — import this everywhere
settings = Settings()
