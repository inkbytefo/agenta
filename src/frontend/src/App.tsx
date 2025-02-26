import { useState } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState('Idle');

  return (
    <div className="container">
      <h1>CrewAI Desktop</h1>
      <div className="card">
        <p>Status: {status}</p>
        <button onClick={() => setStatus('Running...')}>
          Start Task
        </button>
      </div>
    </div>
  );
}

export default App;