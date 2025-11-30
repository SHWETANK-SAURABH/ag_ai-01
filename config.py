"""Configuration management for the Life Admin Task Automator."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with automatic dev mode detection."""
    
    # Gemini API
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Auto-detect dev mode if credentials missing
    DEV_MODE: bool = not bool(GEMINI_API_KEY)
    
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "LifeAdminTaskAutomator")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    MEMORY_DIR: Path = BASE_DIR / "memory" / "storage"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        try:
            cls.DATA_DIR.mkdir(exist_ok=True)
            cls.MEMORY_DIR.mkdir(exist_ok=True)
        except Exception:
            # If directory creation fails (permissions or CI), continue silently
            pass
    
    @classmethod
    def get_mode_status(cls) -> str:
        """Return current operation mode."""
        return "DEVELOPMENT (Mock)" if cls.DEV_MODE else "PRODUCTION (Live API)"


config = Config()
config.ensure_directories()

# Helpful warning if running in dev mode
if config.DEV_MODE:
    import logging
    logging.getLogger(__name__).warning(
        "GEMINI_API_KEY is not set — running in DEVELOPMENT (mock) mode. "
        "Create a .env file with GEMINI_API_KEY to enable PRODUCTION (Live API) mode."
    )