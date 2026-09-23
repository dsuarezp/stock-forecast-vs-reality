"""Load project configuration from YAML, merging local machine overrides."""

from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).parent / "config"


def load_config() -> dict:
    """Load config/config.yaml, merged with config/config.local.yaml if present."""
    config = _load_yaml(CONFIG_DIR / "config.yaml")
    local_path = CONFIG_DIR / "config.local.yaml"
    if local_path.exists():
        config = _deep_merge(config, _load_yaml(local_path))
    return config


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge `override` into `base`, without mutating either."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
