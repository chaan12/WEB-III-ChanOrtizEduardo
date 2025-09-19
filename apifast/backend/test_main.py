from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import mongomock
from pymongo import MongoClient

from main import app

client = TestClient(app)
mongo_client = mongomock.MongoClient()
database = mongo_client.practica1
collection_historial = database.historial

@pytest.mark.parametrize(
        "numeroA, numeroB, resultado",
        [
            (5, 10, 15),
            (0, 0, 0),
            (-5, 5, 0),
            (2.5, 2.5, 5.0),
            (-3, -7, -10),
        ]
)

def test_sumar(numeroA, numeroB, resultado):
    response = client.get(f"/calculadora/sum?a={numeroA}&b={numeroB}")
    assert response.status_code == 200
    assert response.json() == {"a": float(numeroA), "b": float(numeroB), "resultado": float(resultado)}
    assert collection_historial.insert_one.called()
