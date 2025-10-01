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
    <div style={{ padding: 20 }}>
      <h1>Calculadora</h1>
      {numeros.map((num, i) => (
        <input
          key={i}
          type="text"
          inputMode="decimal"
          min="0"
          value={num}
          onChange={(e) => handleNumeroChange(i, e.target.value)}
          placeholder="0"
        />
      ))}
      <button onClick={agregarCampo}>Agregar número</button>
      <div style={{ marginTop: 10 }}>
        <button onClick={sumar}>Sumar</button>
        <button onClick={restar}>Restar</button>
        <button onClick={multiplicar}>Multiplicar</button>
        <button onClick={dividir}>Dividir</button>
      </div>
      {resultado !== null && <h2>Resultado: {resultado}</h2>}

      <h3>Filtros de historial:</h3>
      <div style={{ marginBottom: 10 }}>
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
        <br />
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
        <button onClick={obtenerHistorial}>Aplicar filtros</button>
      </div>
      <p style={{ fontStyle: "italic", color: "gray" }}>
        Puedes combinar <b>Tipo de operación</b> y <b>Fecha</b>.  
        Si seleccionas un ordenamiento, los demás filtros se desactivan automáticamente.
      </p>

      <h3>Historial:</h3>
      {historial.length > 0 ? (
        <ul>
          {historial.map((op, i) => (
            <li key={i}>
              {op.numeros.join(", ")} {op.operacion} = {op.resultado} ({formatDate(op.date)})
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ color: "gray", fontStyle: "italic" }}>
          No hay registros quase coincidan con los filtros seleccionados.
        </p>
      )}
    </div>
  );
}

export default App;
