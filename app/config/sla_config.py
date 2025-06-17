from pathlib import Path
from typing import Dict, Any

from app.config.settings import settings

import yaml


class SLAConfig:
    _config: Dict[str, Any] = {}
    _config_path: Path = Path(settings.SLA_CONFIG_PATH)

    @classmethod
    def load_config(cls) -> None:
        with open(cls._config_path, "r") as f:
            cls._config = yaml.safe_load(f)

    @classmethod
    def get(cls) -> Dict[str, Any]:
        return cls._config
