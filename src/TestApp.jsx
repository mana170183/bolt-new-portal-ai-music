import React, { useState } from 'react'

function App() {
  const [test, setTest] = useState('React is working!')

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'green' }}>🎵 AI Music Generator</h1>
      <p>{test}</p>
      <button 
        onClick={() => setTest('Button clicked! React is interactive!')}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Test React
      </button>
    </div>
  )
}

export default App
