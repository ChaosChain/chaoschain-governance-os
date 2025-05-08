import React from 'react';

interface AttestationBadgeProps {
  attested: boolean;
}

const AttestationBadge: React.FC<AttestationBadgeProps> = ({ attested }) => {
  return (
    <div className="attestation-badge" style={{
      display: 'inline-block',
      padding: '4px 8px',
      borderRadius: '4px',
      backgroundColor: attested ? '#e6f7e6' : '#ffeded',
      color: attested ? '#2e7d32' : '#d32f2f',
      fontWeight: 'bold',
      fontSize: '14px',
      marginLeft: '8px'
    }}>
      {attested ? '✅ Attested' : '❌ Not Attested'}
    </div>
  );
};

export default AttestationBadge; 