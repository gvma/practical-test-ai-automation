import yaml
import os

from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()
sla_config_path = os.getenv("SLA_CONFIG_PATH")
if sla_config_path is None:
    raise RuntimeError("SLA config path is not set.")

class SLAConfig:
    _config: Dict[str, Any] = {}
    _config_path: Path = Path(sla_config_path)

    @classmethod
    def load_config(cls) -> None:
        with open(cls._config_path, "r") as f:
            cls._config = yaml.safe_load(f)

    @classmethod
    def get(cls) -> Dict[str, Any]:
        return cls._config
