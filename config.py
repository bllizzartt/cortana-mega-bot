"""
Configuration for Cortana Mega Bot.
All settings in one place.
"""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Bot configuration."""
    # Telegram
    telegram_bot_token: str = ""
    admin_user_id: int = 0

    # Seedance API (Video Generation)
    seedance_api_key: str = ""
    seedance_api_url: str = "https://api.seedance.example.com/v1"
    mock_mode: bool = True

    # Storage
    video_storage_path: Path = Path("./videos")
    photo_storage_path: Path = Path("./photos")

    # Limits
    max_photos: int = 4
    generation_timeout: int = 300
    status_update_interval: int = 30

    @classmethod
    def load(cls, env_path: Path = None) -> "Config":
        if env_path is None:
            env_path = Path(__file__).parent / ".env"

        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())

        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            admin_user_id=int(os.getenv("ADMIN_USER_ID", "0")),
            seedance_api_key=os.getenv("SEEDANCE_API_KEY", ""),
            seedance_api_url=os.getenv("SEEDANCE_API_URL", "https://api.seedance.example.com/v1"),
            mock_mode=os.getenv("MOCK_MODE", "true").lower() == "true",
            video_storage_path=Path(os.getenv("VIDEO_STORAGE_PATH", "./videos")),
            photo_storage_path=Path(os.getenv("PHOTO_STORAGE_PATH", "./photos")),
            max_photos=int(os.getenv("MAX_PHOTOS", "4")),
            generation_timeout=int(os.getenv("GENERATION_TIMEOUT", "300")),
            status_update_interval=int(os.getenv("STATUS_UPDATE_INTERVAL", "30")),
        )


def get_config() -> Config:
    """Get the bot configuration."""
    return Config.load()
