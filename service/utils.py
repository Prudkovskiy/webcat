import unicodedata

import httpx
import nltk
import numpy as np
import tldextract
from aiocache import cached
from aiocache.serializers import PickleSerializer
from bs4 import BeautifulSoup
from lxml import etree
from nltk.corpus import wordnet as wn
from sentence_transformers import SentenceTransformer
from spacy.lang.en import English

from .config import CATEGORIES_LIST, PROXY_URL, USER_AGENT
from .logger import logger
from .models import (
    EmbeddingURLModel,
    NgramURLModel,
    PastebinModel,
    SiteContentModel,
)

sentence_transformer = SentenceTransformer("all-MPnet-base-v2")


def remove_tld(uri):
    ext = tldextract.extract(uri)
    if ext.subdomain:
        return ".".join(ext[:2])
    return ext.domain


@cached(ttl=60, serializer=PickleSerializer())
async def process_url(url: str, use_proxy: bool = True):
    if not url.startswith("http"):
        url = "http://" + url
    proxies = PROXY_URL if use_proxy and PROXY_URL else None

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15, connect=10, read=5),
        proxies=proxies,
        follow_redirects=True,
        verify=False,
    ) as session:
        response = await session.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        response.encoding = "utf-8"
        # response.myip = (
        #     response.extensions["network_stream"]
        #     .get_extra_info("socket")
        #     .getpeername()[0]
        # )
        return response


def symbol_ngrams(url, n) -> dict[str, bool]:
    ngrams = list(nltk.ngrams(url, n))
    return {"".join(k): True for k in ngrams}


def _drop_tree(el: etree.Element):
    parent = el.getparent()
    if parent is None:
        return
    if el.tail:
        previous = el.getprevious()
        if previous is None:
            parent.text = (parent.text or "") + el.tail
        else:
            previous.tail = (previous.tail or "") + el.tail
    parent.remove(el)


def _normalize_text(text: str) -> str:
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = " ".join(chunk for chunk in chunks if chunk)
    text = unicodedata.normalize("NFKC", text)
    return text


def clean_html(html_tree: etree.ElementTree) -> str:
    html_root = html_tree.getroot()
    if html_root is None:
        return None

    invisible_elements = html_root.xpath(
        ".//*[contains(@style, 'display:none')]"
    )
    for el in invisible_elements:
        _drop_tree(el)

    script_elements = html_root.xpath(".//script|.//style")
    for el in script_elements:
        _drop_tree(el)

    text = _normalize_text(
        etree.tostring(
            html_root,
            encoding="unicode",  # pretty_print=True, method="text"
        )
    )
    return text


def remove_trash(text, min_size=4):
    cleaned = ""
    for i in text.split("\n"):
        if len(i.split()) <= min_size:
            continue
        cleaned += i
    return cleaned


def to_token(text):
    token_list = []
    parser = English()
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace() or token.like_url:
            continue
        if token.orth_.startswith("@") or token.orth_.startswith("#"):
            continue
        if token.is_punct or token.like_num or token.is_stop:
            continue
        token_list.append(token.lower_)

        token_list = [
            wn.morphy(x) if wn.morphy(x) is not None else x for x in token_list
        ]
    return token_list


async def get_html_embedding(url):
    response = await process_url(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = " ".join(to_token(remove_trash(soup.get_text())))
    return sentence_transformer.encode([text])


async def pastebin_predict(url: str):
    domain = remove_tld(url)

    embedding_domain = sentence_transformer.encode([domain])
    url_embed_prediction = PastebinModel.model_url_embed.predict_proba(
        embedding_domain
    )[0][1]

    ngram_dict = symbol_ngrams(domain, 4)
    url_ngram_prediction = PastebinModel.model_url_ngram.prob_classify(
        ngram_dict
    ).prob(1)

    try:
        embedding_pastebin = await get_html_embedding(url)
    except Exception:
        embedding_pastebin = None
        logger.info("can't download content from %s", url)

    if embedding_pastebin is not None:
        text_prediction = PastebinModel.model_text.predict_proba(
            embedding_pastebin
        )[0][1]
        prediction = np.average(
            [
                url_embed_prediction,
                url_ngram_prediction,
                text_prediction,
            ],
            weights=[0.7, 0.8, 1.0],
            axis=0,
        )
    else:
        prediction = np.average(
            [
                url_embed_prediction,
                url_ngram_prediction,
            ],
            weights=[0.7, 0.8],
            axis=0,
        )

    return prediction


async def category_predict(url: str):
    predictions = {}
    domain = remove_tld(url)
    embedding_domain = sentence_transformer.encode([domain])

    try:
        embedding_html = await get_html_embedding(url)
    except Exception:
        embedding_html = None
        logger.info("can't download content from %s", url)

    for category in CATEGORIES_LIST:
        ngram_prediction = NgramURLModel.pipelines[category].predict_proba(
            [domain]
        )[0][1]
        url_prediction = EmbeddingURLModel.pipelines[category].predict_proba(
            embedding_domain
        )[0][1]
        content_prediction = 0
        if embedding_html is not None:
            content_prediction = SiteContentModel.pipelines[
                category
            ].predict_proba(embedding_html)[0][1]

        predictions[category] = round(
            np.average(
                [ngram_prediction, url_prediction, content_prediction],
                weights=[1, 3, 20 if embedding_html is not None else 0],
            ),
            3,
        )

    return dict(
        sorted(predictions.items(), key=lambda item: item[1], reverse=True)[:3]
    )
