import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import AttestationBadge from './AttestationBadge';
import MetricsTable from './MetricsTable';

interface Proposal {
  id: string;
  title: string;
  description: string;
  content: string;
  created_at: string;
  attested: boolean;
  simulation_id: string;
}

const Dashboard: React.FC = () => {
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

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  if (loading) {
    return <div>Loading proposal data...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!proposal) {
    return <div>No proposal found</div>;
  }

  return (
    <div className="dashboard-container" style={{ maxWidth: '900px', margin: '0 auto', padding: '20px' }}>
      <header style={{ marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '24px', margin: '0' }}>{proposal.title}</h1>
          <AttestationBadge attested={proposal.attested} />
        </div>
        <p style={{ color: '#666', marginTop: '8px' }}>
          {proposal.description}
        </p>
        <div style={{ fontSize: '14px', color: '#888', marginTop: '8px' }}>
          Proposed: {formatDate(proposal.created_at)}
        </div>
      </header>
      
      <div className="proposal-content" style={{ 
        backgroundColor: '#fff', 
        padding: '20px', 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <ReactMarkdown>{proposal.content}</ReactMarkdown>
      </div>
      
      <MetricsTable simulationId={proposal.simulation_id} />
    </div>
  );
};

export default Dashboard; 