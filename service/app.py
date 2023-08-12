import os
import ssl
from io import BytesIO

import httpx
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from lxml import etree

from src.models.serialize import load

from .config import MODEL_MYIP_URL_PATH, NUM_CATEGORIES
from .logger import logger
from .models import (
    EmbeddingURLModel,
    MyIpModel,
    NgramURLModel,
    PastebinModel,
    SiteContentModel,
    URLChecker,
)
from .utils import (
    category_predict,
    clean_html,
    pastebin_predict,
    process_url,
    remove_tld,
)

app = FastAPI()


@app.on_event("startup")
async def load_model():
    # response = await process_url("https://www.wikipedia.org", use_proxy=False)
    # MyIpModel.ip = response.headers.get("X-Client-IP")
    MyIpModel.pipeline = load("myip_url.joblib", path=MODEL_MYIP_URL_PATH)

    filepath = "models/pastebin_models/"
    PastebinModel.model_text = load("request_text_classifier.pkl", filepath)
    PastebinModel.model_url_embed = load("text_url_classifier.pkl", filepath)
    PastebinModel.model_url_ngram = load("ngram_classifier.pkl", filepath)

    filepath = "models/ngram_models_light/"
    for root, _, files in os.walk(filepath):
        for filename in files:
            category = filename.split(".")[0]
            NgramURLModel.pipelines[category] = load(filename, root)

    filepath = "models/url_models/"
    for root, _, files in os.walk(filepath):
        for filename in files:
            category = filename.split(".")[0]
            EmbeddingURLModel.pipelines[category] = load(filename, root)

    filepath = "models/request_models/"
    for root, _, files in os.walk(filepath):
        for filename in files:
            category = filename.split(".")[0]
            SiteContentModel.pipelines[category] = load(filename, root)


@app.get("/")
def read_healthcheck():
    return {"status": "Green"}


async def check_pastebin(uri: str):
    pred = await pastebin_predict(uri)
    return {"probability": round(pred, 3)}


async def check_myip(uri: str):
    try:
        response = await process_url(uri, use_proxy=False)
        logger.info("process %s successful", uri)
    except (httpx.HTTPError, ssl.SSLError) as ex:
        logger.error(ex)
        response = None

    if response is not None:
        parser = etree.HTMLParser(encoding="utf-8")
        tree = etree.parse(BytesIO(response.text.encode()), parser)
        text = clean_html(tree)
        if response.myip in text:
            return {"probability": 1, "check_in_content": True}

    data = [remove_tld(uri)]
    if MyIpModel.pipeline is None:
        raise HTTPException(status_code=503, detail="No model loaded")

    pred = MyIpModel.pipeline.predict_proba(data)[0][1]
    logger.info("probability for %s is %.2f", uri, pred)
    return {"probability": round(pred, 3), "check_in_content": False}


async def check_category(uri: str):
    if len(NgramURLModel.pipelines) != NUM_CATEGORIES:
        raise HTTPException(
            status_code=503, detail="Some ngram models are missing"
        )
    if len(EmbeddingURLModel.pipelines) != NUM_CATEGORIES:
        raise HTTPException(
            status_code=503, detail="Some url_embeddings models are missing"
        )
    try:
        predictions = await category_predict(uri)

    except Exception as ex:
        logger.exception(str(ex))
        raise HTTPException(status_code=400, detail=str(ex))

    return predictions


@app.post("/check_url")
async def check_url(request: URLChecker):
    result: dict = {}
    result["categories"] = await check_category(request.uri)
    if request.check_pastebin is True:
        result["pastebin"] = await check_pastebin(request.uri)
    if request.check_ip is True:
        result["myip"] = await check_myip(request.uri)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
