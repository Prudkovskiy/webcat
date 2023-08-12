# from lightgbm import LGBMClassifier
from nltk.classify import NaiveBayesClassifier
from pydantic import BaseModel
from sklearn.pipeline import Pipeline


class MyIpModel:
    pipeline: Pipeline | None = None
    # ip: str | None = None


class PastebinModel:
    model_url_embed: NaiveBayesClassifier | None = None
    model_url_ngram: NaiveBayesClassifier | None = None
    model_text: NaiveBayesClassifier | None = None


class NgramURLModel:
    pipelines: dict[str, Pipeline] = {}


class EmbeddingURLModel:
    pipelines: dict[str, Pipeline] = {}


class SiteContentModel:
    pipelines: dict[str, Pipeline] = {}


class URLChecker(BaseModel):
    uri: str
    check_ip: bool = True
    check_pastebin: bool = True
