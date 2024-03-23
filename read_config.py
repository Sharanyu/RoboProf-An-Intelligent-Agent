import yaml
import os
from pathlib import Path


def load_config():
    with open("rbp_config.yaml", "r") as f:
        config = yaml.safe_load(f)
        return config


def normalize_path(path):
    return os.path.normpath(path)
