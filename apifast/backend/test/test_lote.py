import os
import sys
import pytest
import mongomock
from fastapi.testclient import TestClient

# Permitir importación de main.py
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import main
from main import app

client = TestClient(app)

@pytest.fixture
def fake_collection_historial():
    fake_mongo_client = mongomock.MongoClient()
    fake_database = fake_mongo_client["test_database"]
    return fake_database["historial"]

def test_lote_operaciones_validas(monkeypatch, fake_collection_historial):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    payload = [
        {"op": "sum", "nums": [2, 3]},
        {"op": "sub", "nums": [5, 2]},
        {"op": "mul", "nums": [3, 4]},
        {"op": "div", "nums": [10, 2]},
    ]
    r = client.post("/calculadora/lote", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data[0]["result"] == 5
    assert data[1]["result"] == 3
    assert data[2]["result"] == 12
    assert data[3]["result"] == 5

def test_lote_con_negativos(monkeypatch, fake_collection_historial):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    payload = [
        {"op": "sum", "nums": [-1, 3]}
    ]
    r = client.post("/calculadora/lote", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "error" in data[0]
    assert "negativos" in data[0]["error"]

def test_lote_division_cero(monkeypatch, fake_collection_historial):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    payload = [
        {"op": "div", "nums": [10, 0]}
    ]
    r = client.post("/calculadora/lote", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "error" in data[0]
    assert "No se puede dividir entre cero" in data[0]["error"]

def test_lote_operacion_no_soportada(monkeypatch, fake_collection_historial):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    payload = [
        {"op": "pow", "nums": [2, 3]}
    ]
    r = client.post("/calculadora/lote", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "error" in data[0]
    assert "Operación no soportada" in data[0]["error"]

def test_lote_operandos_invalidos(monkeypatch, fake_collection_historial):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    payload = [
        {"op": "sum", "nums": [1]}
    ]
    r = client.post("/calculadora/lote", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "error" in data[0]
    assert "exactamente 2 operandos" in data[0]["error"]