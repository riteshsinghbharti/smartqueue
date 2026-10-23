import React from 'react';

export default function ClinicalFooter() {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-light)',
      background: '#ffffff',
      padding: '1.25rem 1.5rem',
      fontSize: '0.72rem',
      color: 'var(--text-muted)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      flexWrap: 'wrap',
      gap: '0.75rem'
    }} className="mono">
      <div>KRONOS HEALTH LABS • Clinical Queue System v4.12</div>
      <div>HIPAA COMPLIANT ENVIRONMENT • © 2025 Kronos Clinical Systems</div>
    </footer>
  );
}
