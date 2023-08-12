import os
from pathlib import Path

import dvc.api
import joblib
from sklearn.pipeline import Pipeline

from service.config import CONFIG_S3
from service.logger import logger

__all__ = ["store", "load"]


def store(pipeline: Pipeline, filename: str, path: str = "default"):
    if path == "default":
        path = models_path()
    else:
        path = Path(path)
    filepath = path / filename
    logger.info("Dumpung model into %s", filepath)
    joblib.dump(pipeline, filepath)


def load(filename: str, path: str = "default") -> Pipeline:
    if path == "default":
        path = models_path()
    else:
        path = Path(path)
    filepath = path / filename
    logger.info("Loading model from %s", filepath)
    return joblib.load(filepath)


def load_from_s3(filename: str, path: str = "models") -> Pipeline:
    filepath = os.path.join(path, filename)
    with dvc.api.open(
        filepath,
        config=CONFIG_S3,
        mode="rb",
    ) as f:
        model = joblib.load(f)
    return model


def models_path() -> str:
    return Path(__file__).parents[2] / "models"
