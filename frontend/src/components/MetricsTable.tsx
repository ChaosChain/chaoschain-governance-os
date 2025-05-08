import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface SimulationMetric {
  name: string;
  value: number;
  unit: string;
  change: number;
}

interface MetricsTableProps {
  simulationId: string;
}

const MetricsTable: React.FC<MetricsTableProps> = ({ simulationId }) => {
  const [metrics, setMetrics] = useState<SimulationMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSimulationData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/simulations/${simulationId}`);
        
        // If there's no metrics data in the response, use default data for demo
        if (!response.data || !response.data.metrics) {
          setMetrics([
            { name: 'Gas Used Ratio', value: 0.68, unit: '', change: -0.14 },
            { name: 'Base Fee', value: 18.7, unit: 'gwei', change: -4.8 },
            { name: 'Fee Volatility', value: 0.47, unit: '', change: -0.21 },
            { name: 'Throughput', value: 14.3, unit: 'tx/s', change: 2.1 },
            { name: 'Block Utilization', value: 72.5, unit: '%', change: 7.5 }
          ]);
        } else {
          setMetrics(response.data.metrics);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching simulation data:', err);
        setError('Failed to load simulation metrics');
        setLoading(false);
        
        // Use mock data for demo if fetch fails
        setMetrics([
          { name: 'Gas Used Ratio', value: 0.68, unit: '', change: -0.14 },
          { name: 'Base Fee', value: 18.7, unit: 'gwei', change: -4.8 },
          { name: 'Fee Volatility', value: 0.47, unit: '', change: -0.21 },
          { name: 'Throughput', value: 14.3, unit: 'tx/s', change: 2.1 },
          { name: 'Block Utilization', value: 72.5, unit: '%', change: 7.5 }
        ]);
      }
    };

    fetchSimulationData();
  }, [simulationId]);

  if (loading) {
    return <div>Loading simulation metrics...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="metrics-table-container" style={{ margin: '20px 0' }}>
      <h3>Simulation Metrics</h3>
      <table style={{ 
        width: '100%', 
        borderCollapse: 'collapse',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <thead>
          <tr style={{ backgroundColor: '#f5f5f5' }}>
            <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: '1px solid #eee' }}>Metric</th>
            <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: '1px solid #eee' }}>Value</th>
            <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: '1px solid #eee' }}>Change</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric, index) => (
            <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#fff' : '#fafafa' }}>
              <td style={{ padding: '12px 16px', borderBottom: '1px solid #eee' }}>{metric.name}</td>
              <td style={{ padding: '12px 16px', textAlign: 'right', borderBottom: '1px solid #eee' }}>
                {metric.value.toFixed(2)} {metric.unit}
              </td>
              <td style={{ 
                padding: '12px 16px', 
                textAlign: 'right', 
                borderBottom: '1px solid #eee',
                color: metric.change > 0 ? '#2e7d32' : metric.change < 0 ? '#d32f2f' : 'inherit'
              }}>
                {metric.change > 0 ? '+' : ''}{metric.change.toFixed(2)} {metric.unit}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MetricsTable; 