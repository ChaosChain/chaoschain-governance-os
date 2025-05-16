import React from 'react';
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

interface ProposalViewProps {
  proposal: Proposal | null;
  loading: boolean;
  error: string | null;
}

const ProposalView: React.FC<ProposalViewProps> = ({ proposal, loading, error }) => {
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
    <div className="proposal-view-container" style={{ 
      height: '100%', 
      overflowY: 'auto',
      padding: '0 15px'
    }}>
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
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <ReactMarkdown>{proposal.content}</ReactMarkdown>
      </div>
      
      <MetricsTable simulationId={proposal.simulation_id} />
    </div>
  );
};

export default ProposalView; 