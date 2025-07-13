import React from 'react'
import ReactDOM from 'react-dom/client'

function SimpleApp() {
  return (
    <div style={{
      padding: '40px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        🎵 AI Music Generator - Test Mode
      </h1>
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <p style={{ fontSize: '18px', color: '#666' }}>
          ✅ React is working correctly!
        </p>
        <button 
          onClick={() => {
            fetch('http://localhost:5001/health')
              .then(r => r.json())
              .then(data => alert('Backend connected: ' + data.message))
              .catch(e => alert('Backend error: ' + e.message))
          }}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Test Backend Connection
        </button>
      </div>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<SimpleApp />)
