import "./App.css";
import React, { useState, useEffect } from "react";

function App() {
  const [numeros, setNumeros] = useState([""]);
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState([]);

  // Filtros para historial
  const [filtroOperacion, setFiltroOperacion] = useState("");
  const [fecha, setFecha] = useState("");
  const [ordenFecha, setOrdenFecha] = useState("");
  const [ordenResultado, setOrdenResultado] = useState("");

  const handleNumeroChange = (index, value) => {
    // Permitir solo números enteros o decimales positivos
    if (!/^\d*\.?\d*$/.test(value)) return;

    const nuevos = [...numeros];
    nuevos[index] = value;
    setNumeros(nuevos);
  };

  const agregarCampo = () => {
    setNumeros([...numeros, ""]);
  };

  // Función generalizada para llamar a la API con POST y JSON body
  const llamarAPI = async (endpoint) => {
    const res = await fetch(`http://localhost:8089${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ numeros: numeros.map(Number) }),
    });
    const data = await res.json();
    if (res.ok) {
      setResultado(data.resultado);
      obtenerHistorial();
    } else {
      alert(data.detail || data.error);
    }
  };

  const sumar = () => llamarAPI("/calculadora/sum");
  const restar = () => llamarAPI("/calculadora/resta");
  const multiplicar = () => llamarAPI("/calculadora/multiplicacion");
  const dividir = () => llamarAPI("/calculadora/division");

  // Obtener historial con filtros opcionales
  const obtenerHistorial = async () => {
    const params = new URLSearchParams();
    if (filtroOperacion) params.append("operacion", filtroOperacion);
    if (fecha) {
      const start = new Date(`${fecha}T00:00:00`);
      const end = new Date(`${fecha}T23:59:59.999`);
      params.append("fecha_inicio", start.toISOString());
      params.append("fecha_fin", end.toISOString());
    }
    if (ordenFecha) params.append("orden_fecha", ordenFecha);
    if (ordenResultado) params.append("orden_resultado", ordenResultado);
    const res = await fetch(
      `http://localhost:8089/calculadora/historial?${params.toString()}`
    );
    const data = await res.json();
    setHistorial(data.historial);
  };

  // Ejecutar historial cada vez que cambie un filtro
  useEffect(() => {
    obtenerHistorial();
    // eslint-disable-next-line
  }, [filtroOperacion, fecha, ordenFecha, ordenResultado]);

  // Helper to format ISO date as DD/MM/YYYY
  const formatDate = (isoString) => {
    if (!isoString) return "";
    const d = new Date(isoString);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  };

  return (
    <div className="app-container">
      <h1 className="title">ChanCalculadora</h1>
      <div className="calc-card">
        {numeros.map((num, i) => (
          <input
            key={i}
            type="text"
            inputMode="decimal"
            min="0"
            value={num}
            onChange={(e) => handleNumeroChange(i, e.target.value)}
            placeholder="0"
            className="num-input"
          />
        ))}
        <div className="add-btn-container">
          <button className="btn add-btn btn-fixed" onClick={agregarCampo}>
            Agregar número
          </button>
        </div>
        <div className="btn-group">
          <button className="btn primary" onClick={sumar}>Sumar</button>
          <button className="btn warning" onClick={restar}>Restar</button>
          <button className="btn success" onClick={multiplicar}>Multiplicar</button>
          <button className="btn danger" onClick={dividir}>Dividir</button>
        </div>
        {resultado !== null && (
          <div className="result">
            <span>Resultado: </span>
            <b>{resultado}</b>
          </div>
        )}
      </div>

      <div className="filter-card">
        <h3>Filtros de historial:</h3>
        <div className="filters">
          <select
            value={filtroOperacion}
            onChange={e => {
              setFiltroOperacion(e.target.value);
              setOrdenFecha("");
              setOrdenResultado("");
            }}
          >
            <option value="">Todas</option>
            <option value="suma">Suma</option>
            <option value="resta">Resta</option>
            <option value="multiplicacion">Multiplicación</option>
            <option value="division">División</option>
          </select>
          <input
            type="date"
            value={fecha}
            onChange={e => {
              setFecha(e.target.value);
              setOrdenFecha("");
              setOrdenResultado("");
            }}
          />
          <select
            value={ordenFecha}
            onChange={e => {
              setOrdenFecha(e.target.value);
              setFiltroOperacion("");
              setFecha("");
              setOrdenResultado("");
            }}
          >
            <option value="asc">Fecha Ascendente</option>
            <option value="desc">Fecha Descendente</option>
          </select>
          <select
            value={ordenResultado}
            onChange={e => {
              setOrdenResultado(e.target.value);
              setFiltroOperacion("");
              setFecha("");
              setOrdenFecha("");
            }}
          >
            <option value="asc">Resultado Ascendente</option>
            <option value="desc">Resultado Descendente</option>
          </select>
        </div>
        <p className="filters-hint">
          Puedes combinar <b>Tipo de operación</b> y <b>Fecha</b>.  
          Si seleccionas un ordenamiento, los demás filtros se desactivan automáticamente.
        </p>
      </div>

      <h3>Historial:</h3>
      {historial.length > 0 ? (
        <table className="hist-table">
          <thead>
            <tr>
              <th>Números</th>
              <th>Operación</th>
              <th>Resultado</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {historial.map((op, i) => (
              <tr key={i}>
                <td>{op.numeros.join(", ")}</td>
                <td>{op.operacion}</td>
                <td>{op.resultado}</td>
                <td>{formatDate(op.date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="no-data">
          🚫 No hay registros que coincidan con los filtros seleccionados.
        </p>
      )}
    </div>
  );
}

export default App;
