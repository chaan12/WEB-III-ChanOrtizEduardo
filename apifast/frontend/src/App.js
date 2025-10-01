import "./App.css";
import React, { useState, useEffect } from "react";

function App() {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState([]);

  const sumar = async () => {
    const res = await fetch("http://localhost:8089/calculadora/sum", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        numeros: [parseFloat(a), parseFloat(b)],
      }),
    });
    const data = await res.json();
    setResultado(data.resultado);
    obtenerHistorial();
  };

  const obtenerHistorial = async () => {
    const res = await fetch("http://localhost:8089/calculadora/historial");
    const data = await res.json();
    setHistorial(data.historial);
  };

  useEffect(() => {
    obtenerHistorial();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Calculadora</h1>
      <input
        type="number"
        value={a}
        onChange={(e) => setA(e.target.value)}
        placeholder="Número Numero"
      />
      <input
        type="number"
        value={b}
        onChange={(e) => setB(e.target.value)}
        placeholder="Número Numero 2"
      />
      <button onClick={sumar}>Sumar</button>
      {resultado !== null && <h2>Resultado: {resultado}</h2>}
      <h3>Historial:</h3>
      <ul>
        {historial.map((op, i) => (
          <li key={i}>
            {op.numeros && Array.isArray(op.numeros)
              ? op.numeros.join(" + ")
              : ""}{" "}
            = {op.resultado} ({op.date})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
