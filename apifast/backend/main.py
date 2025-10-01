import os
import datetime
import logging
from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_uri = os.getenv("MONGO_URI", "mongodb://admin_user:web3@mongo:27017/")
mongo_client = MongoClient(mongo_uri)
database = mongo_client.practica1
collection_historial = database.historial

class Operacion(BaseModel):
    numeros: List[float]

    @field_validator("numeros", mode="before")
    def validar_numeros(cls, v):
        if isinstance(v, list):
            for n in v:
                if not isinstance(n, (int, float)):
                    raise ValueError("Solo se permiten números")
            return v
        if not isinstance(v, (int, float)):
            raise ValueError("Solo se permiten números")
        return v

class LoteOperacion(BaseModel):
    op: str
    nums: List[float]

    @field_validator("nums", mode="before")
    def validar_numeros(cls, v):
        if isinstance(v, list):
            for n in v:
                if not isinstance(n, (int, float)):
                    raise ValueError("Solo se permiten números")
            return v
        if not isinstance(v, (int, float)):
            raise ValueError("Solo se permiten números")
        return v

def insertar_historial(numeros, resultado, operacion):
    document = {
        "numeros": numeros,
        "resultado": resultado,
        "operacion": operacion,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)
    logging.info(f"guardado: {numeros} = {resultado} ({operacion})")

def validar_operandos(numeros, operacion):
    if len(numeros) < 2:
        logging.warning(f"mal: se necesitan al menos 2 operandos -> {numeros}")
        raise HTTPException(status_code=400, detail="Se requieren al menos 2 operandos")
    for n in numeros:
        if n < 0:
            logging.warning(f"mal: num negativo en {numeros}")
            raise HTTPException(status_code=400, detail="No se permiten números negativos")
    if (operacion in ("division","div")) and 0 in numeros[1:]:
        logging.warning(f"mal: div 0 -> {numeros}")
        raise HTTPException(status_code=403, detail="No se puede dividir entre cero")

@app.post("/calculadora/sum")
def sumar(data: Operacion):
    logging.info("sumando...")
    validar_operandos(data.numeros, "sum")
    result = sum(data.numeros)
    insertar_historial(data.numeros, result, "suma")
    return {"numeros": data.numeros, "resultado": result}

@app.post("/calculadora/resta")
def restar(data: Operacion):
    logging.info("restando...")
    validar_operandos(data.numeros, "sub")
    result = data.numeros[0]
    for n in data.numeros[1:]:
        result -= n
    insertar_historial(data.numeros, result, "resta")
    return {"numeros": data.numeros, "resultado": result}

@app.post("/calculadora/multiplicacion")
def multiplicar(data: Operacion):
    logging.info("multiplicando...")
    validar_operandos(data.numeros, "mul")
    result = 1
    for n in data.numeros:
        result *= n
    insertar_historial(data.numeros, result, "multiplicacion")
    return {"numeros": data.numeros, "resultado": result}

@app.post("/calculadora/division")
def dividir(data: Operacion):
    logging.info("dividiendo...")
    validar_operandos(data.numeros, "div")
    result = data.numeros[0]
    for n in data.numeros[1:]:
        if n == 0:
            return {"error": "Division by zero", "operacion": "div", "operandos": data.numeros}
        result /= n
    insertar_historial(data.numeros, result, "division")
    return {"numeros": data.numeros, "resultado": result}

def _rango_dia_utc(fecha_str: str):
    try:
        if "T" in fecha_str:
            dt = datetime.datetime.fromisoformat(fecha_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            d = dt.astimezone(datetime.timezone.utc).date()
        else:
            d = datetime.date.fromisoformat(fecha_str)
        inicio = datetime.datetime.combine(d, datetime.time(0, 0, 0, 0, tzinfo=datetime.timezone.utc))
        fin = inicio + datetime.timedelta(days=1) - datetime.timedelta(microseconds=1)
        return inicio, fin
    except Exception:
        return None, None

def _parse_iso_maybe_z(s: str):
    try:
        if not s:
            return None
        s = s.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None

@app.get("/calculadora/historial")
def obtener_historial(
    operacion: str = Query(None),
    fecha: str = Query(None),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    orden_fecha: str = Query(None), 
    orden_resultado: str = Query(None),
):
    if (orden_fecha or orden_resultado) and (operacion and (fecha or fecha_inicio or fecha_fin)):
        orden_fecha = None
        orden_resultado = None

    query = {}
    if operacion:
        query["operacion"] = operacion

    rango_especifico = False
    if fecha_inicio or fecha_fin:
        start_dt = _parse_iso_maybe_z(fecha_inicio) if fecha_inicio else None
        end_dt = _parse_iso_maybe_z(fecha_fin) if fecha_fin else None
        rango = {}
        if start_dt:
            rango["$gte"] = start_dt
        if end_dt:
            rango["$lte"] = end_dt
        if rango:
            query["date"] = rango
            rango_especifico = True
            if orden_fecha:
                orden_fecha = None

    if not rango_especifico and fecha:
        inicio, fin = _rango_dia_utc(fecha)
        if inicio and fin:
            query["date"] = {"$gte": inicio, "$lte": fin}
            if orden_fecha:
                orden_fecha = None

    sort_fields = []
    if orden_fecha in ("asc", "desc"):
        sort_fields.append(("date", 1 if orden_fecha == "asc" else -1))
    if orden_resultado in ("asc", "desc"):
        sort_fields.append(("resultado", 1 if orden_resultado == "asc" else -1))

    cursor = collection_historial.find(query)
    if sort_fields:
        cursor = cursor.sort(sort_fields)
    else:
        cursor = cursor.sort("date", -1)

    historial = []
    for op in cursor:
        historial.append({
            "numeros": op.get("numeros", []),
            "resultado": op["resultado"],
            "operacion": op.get("operacion", ""),
            "date": op.get("date").isoformat() if isinstance(op.get("date"), datetime.datetime) else str(op.get("date"))
        })
    return {"historial": historial}

@app.post("/calculadora/lote")
def calcular_lote(ops: List[LoteOperacion]):
    logging.info("procesando lote...")
    resultados = []
    for op in ops:
        try:
            validar_operandos(op.nums, op.op)
        except HTTPException as e:
            resultados.append({"error": e.detail, "operacion": op.op, "operandos": op.nums})
            continue
        if op.op == "sum":
            res = sum(op.nums)
        elif op.op == "sub":
            res = op.nums[0]
            for n in op.nums[1:]:
                res -= n
        elif op.op == "mul":
            res = 1
            for n in op.nums:
                res *= n
        elif op.op == "div":
            res = op.nums[0]
            try:
                for n in op.nums[1:]:
                    if n == 0:
                        raise ZeroDivisionError
                    res /= n
            except ZeroDivisionError:
                resultados.append({"error": "Division by zero", "operacion": "div", "operandos": op.nums})
                continue
        else:
            resultados.append({"error": "Operación no soportada", "operacion": op.op, "operandos": op.nums})
            continue
        insertar_historial(op.nums, res, op.op)
        resultados.append({"op": op.op, "result": res})
    return resultados