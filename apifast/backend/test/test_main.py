import os
import sys
import pytest
import mongomock
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import main
from main import app

client = TestClient(app)

fake_mongo_client = mongomock.MongoClient()
fake_database = fake_mongo_client["testdb"]
fake_collection_historial = fake_database["historial"]

@pytest.mark.parametrize("endpoint,a,b,expected", [
    ("/calculadora/sum", 10, 5, 15),
    ("/calculadora/resta", 10, 5, 5),
    ("/calculadora/multiplicacion", 10, 5, 50),
    ("/calculadora/division", 10, 5, 2.0),
])
def test_operaciones_validas(monkeypatch, endpoint, a, b, expected):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    r = client.post(endpoint, json={"numeros": [a, b]})
    assert r.status_code == 200
    data = r.json()
    assert data["resultado"] == pytest.approx(expected)

@pytest.mark.parametrize("endpoint", [
    "/calculadora/sum",
    "/calculadora/resta",
    "/calculadora/multiplicacion",
    "/calculadora/division",
])
def test_operaciones_con_negativos(monkeypatch, endpoint):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    r = client.post(endpoint, json={"numeros": [-1, 5]})
    assert r.status_code == 400
    assert "negativos" in r.json()["detail"]

def test_division_por_cero(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    r = client.post("/calculadora/division", json={"numeros": [9, 0]})
    assert r.status_code == 403
    assert "dividir entre cero" in r.json()["detail"]