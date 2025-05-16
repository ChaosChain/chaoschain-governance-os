import { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css'
import LiveFeed from './components/LiveFeed'
import ProposalView from './components/ProposalView'

interface Proposal {
  id: string;
  title: string;
  description: string;
  content: string;
  created_at: string;
  attested: boolean;
  simulation_id: string;
}

function App() {
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLatestProposal = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/proposals/last');
        
        if (response.data) {
          setProposal(response.data);
        } else {
          // Use mock data for demo if no proposal found
          setProposal({
            id: "demo-proposal-001",
            title: "EIP-1559 Parameter Optimization",
            description: "Proposal to optimize gas parameters based on recent network analysis",
            content: `# Parameter Optimization Proposal

## Overview
Based on the gas metrics analysis, I propose the following parameter adjustments to 
improve throughput and fee predictability.

## Proposed Parameters
1. Gas Limit Adjustment: +15%
   - Current: ~30M gas/block
   - Proposed: ~34.5M gas/block
   
2. Base Fee Adjustment: 0.85x current rate
   - Reduces the intensity of base fee changes during demand spikes
   
3. EIP-1559 Adjustment Quotient: 12 (currently 8)
   - Makes fee changes more gradual and predictable
   
4. Target Block Utilization: 0.75 (currently 0.5)
   - Sets optimal gas used ratio for the network

## Expected Benefits
- Improved fee predictability (est. 15% reduction in volatility)
- Higher throughput during peak demand (+10-12%)
- Better user experience due to more consistent transaction confirmation times
- More efficient market for block space

## Risks and Mitigations
- Risk: Higher gas limit could increase state growth rate
  - Mitigation: Monitor state growth and adjust if necessary
  
- Risk: More gradual fee adjustment could lead to longer periods of congestion
  - Mitigation: The higher gas limit compensates by providing more capacity

## Simulation Results
Simulations show these parameters would have reduced average fees by 8.5% during 
the last network congestion event, while increasing transaction throughput by 11.2%.

The parameters were tested against historical data from the past 3 months and 
demonstrated consistent improvements in both normal and high-demand scenarios.`,
            created_at: new Date().toISOString(),
            attested: true,
            simulation_id: "demo-sim-001"
          });
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching latest proposal:', err);
        setError('Failed to load the latest proposal');
        setLoading(false);
        
        // Use mock data for demo if fetch fails
        setProposal({
          id: "demo-proposal-001",
          title: "EIP-1559 Parameter Optimization",
          description: "Proposal to optimize gas parameters based on recent network analysis",
          content: `# Parameter Optimization Proposal

## Overview
Based on the gas metrics analysis, I propose the following parameter adjustments to 
improve throughput and fee predictability.

## Proposed Parameters
1. Gas Limit Adjustment: +15%
   - Current: ~30M gas/block
   - Proposed: ~34.5M gas/block
   
2. Base Fee Adjustment: 0.85x current rate
   - Reduces the intensity of base fee changes during demand spikes
   
3. EIP-1559 Adjustment Quotient: 12 (currently 8)
   - Makes fee changes more gradual and predictable
   
4. Target Block Utilization: 0.75 (currently 0.5)
   - Sets optimal gas used ratio for the network

## Expected Benefits
- Improved fee predictability (est. 15% reduction in volatility)
- Higher throughput during peak demand (+10-12%)
- Better user experience due to more consistent transaction confirmation times
- More efficient market for block space

## Risks and Mitigations
- Risk: Higher gas limit could increase state growth rate
  - Mitigation: Monitor state growth and adjust if necessary
  
- Risk: More gradual fee adjustment could lead to longer periods of congestion
  - Mitigation: The higher gas limit compensates by providing more capacity

## Simulation Results
Simulations show these parameters would have reduced average fees by 8.5% during 
the last network congestion event, while increasing transaction throughput by 11.2%.

The parameters were tested against historical data from the past 3 months and 
demonstrated consistent improvements in both normal and high-demand scenarios.`,
          created_at: new Date().toISOString(),
          attested: true,
          simulation_id: "demo-sim-001"
        });
      }
    };

    fetchLatestProposal();
  }, []);

  return (
    <div className="app">
      <header className="app-header" style={{
        backgroundColor: '#1a1a2e',
        color: 'white',
        padding: '16px 0',
        marginBottom: '16px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <h1 style={{ margin: 0, fontSize: '28px' }}>ChaosChain Governance OS</h1>
          <p style={{ margin: '8px 0 0', opacity: 0.8 }}>AI-Powered Blockchain Governance</p>
        </div>
      </header>
      
      <main style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '0 20px',
        display: 'flex',
        gap: '20px',
        minHeight: 'calc(100vh - 200px)'
      }}>
        {/* Live Feed (35%) */}
        <div style={{ width: '35%', borderRight: '1px solid #eee', paddingRight: '20px' }}>
          <LiveFeed />
        </div>
        
        {/* Proposal & Simulation (65%) */}
        <div style={{ width: '65%' }}>
          <ProposalView 
            proposal={proposal}
            loading={loading}
            error={error}
          />
        </div>
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
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          ChaosChain Governance OS &copy; {new Date().getFullYear()} | Demo Version
        </div>
      </footer>
    </div>
  )
}

export default App
