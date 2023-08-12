import pytest
from fastapi.testclient import TestClient

from service.app import app
from service.models import MyIpModel
from src.models.serialize import load

client = TestClient(app)


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Green"


# @pytest.mark.parametrize(
#     "uri,expected",
#     [
#         ("http://checkip.dns.he.net", 0.9),
#         ("http://dawhois.com", 0.5),
#         ("http://myip.com", 1),
#     ],
# )
# def test_predict(uri, expected):
#     pipeline = load("my_ip_models/myip_url.joblib")
#     MyIpModel.pipeline = pipeline

#     passenger = {"uri": uri}
#     response = client.post("/check_url", json=passenger)
#     assert response.status_code == 200
#     assert response.json() == {"probability": expected}
