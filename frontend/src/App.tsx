import './App.css'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="app">
      <header className="app-header" style={{
        backgroundColor: '#1a1a2e',
        color: 'white',
        padding: '16px 0',
        marginBottom: '24px'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', padding: '0 20px' }}>
          <h1 style={{ margin: 0, fontSize: '28px' }}>ChaosChain Governance OS</h1>
          <p style={{ margin: '8px 0 0', opacity: 0.8 }}>AI-Powered Blockchain Governance</p>
        </div>
      </header>
      
      <main>
        <Dashboard />
      </main>
      
      <footer style={{
        margin: '40px 0 0',
        padding: '20px',
        backgroundColor: '#f5f5f5',
        borderTop: '1px solid #eee',
        textAlign: 'center',
        color: '#666',
        fontSize: '14px'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          ChaosChain Governance OS &copy; {new Date().getFullYear()} | Demo Version
        </div>
      </footer>
    </div>
  )
}

export default App
