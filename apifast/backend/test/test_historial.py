

import os
import sys
import pytest
import datetime
import mongomock
from pymongo import MongoClient
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import main

fake_mongo_client = mongomock.MongoClient()
fake_database = fake_mongo_client["calculadora_test"]
fake_collection_historial = fake_database["historial"]

def setup_module(module):
    fake_collection_historial.delete_many({})

    base_date = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)
    docs = [
        {"numeros": [2, 3], "resultado": 5, "operacion": "suma", "date": base_date},
        {"numeros": [5, 2], "resultado": 3, "operacion": "resta", "date": base_date + datetime.timedelta(days=1)},
        {"numeros": [3, 4], "resultado": 12, "operacion": "multiplicacion", "date": base_date + datetime.timedelta(days=2)},
        {"numeros": [10, 2], "resultado": 5, "operacion": "division", "date": base_date + datetime.timedelta(days=3)},
    ]
    fake_collection_historial.insert_many(docs)

def test_filtrar_por_operacion(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    client = TestClient(main.app)

    r = client.get("/calculadora/historial", params={"operacion": "suma"})
    assert r.status_code == 200
    data = r.json()["historial"]
    assert all(item["operacion"] == "suma" for item in data)

def test_ordenar_por_resultado_desc(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    client = TestClient(main.app)

    r = client.get("/calculadora/historial", params={"orden_resultado": "desc"})
    assert r.status_code == 200
    data = r.json()["historial"]
    resultados = [item["resultado"] for item in data]
    assert resultados == sorted(resultados, reverse=True)

def test_filtrar_por_fecha(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)
    client = TestClient(main.app)

    fecha_inicio = "2023-01-02T00:00:00+00:00"
    fecha_fin = "2023-01-03T23:59:59+00:00"
    r = client.get("/calculadora/historial", params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
    assert r.status_code == 200
    data = r.json()["historial"]
    assert all("2023-01-02" <= item["date"][:10] <= "2023-01-03" for item in data)