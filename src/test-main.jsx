import React from 'react'
import ReactDOM from 'react-dom/client'

// Minimal test component
function TestApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'green' }}>✅ React App is Working!</h1>
      <p>If you can see this, React is rendering correctly.</p>
      <button 
        onClick={() => alert('React is interactive!')}
        style={{ padding: '10px 20px', fontSize: '16px' }}
      >
        Test Interaction
      </button>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<TestApp />)
