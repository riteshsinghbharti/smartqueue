import React from 'react';

export default function AdminQueueTable({ waitingPatients, onCall, loading }) {
  if (waitingPatients.length === 0) {
    return (
      <div className="mono" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        QUEUE CLEAR • NO PATIENTS CURRENTLY WAITING
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
        <thead>
          <tr className="mono" style={{ borderBottom: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '0.72rem' }}>
            <th style={{ padding: '0.75rem' }}>TOKEN</th>
            <th style={{ padding: '0.75rem' }}>PATIENT NAME</th>
            <th style={{ padding: '0.75rem' }}>AGE / SEX</th>
            <th style={{ padding: '0.75rem' }}>SYMPTOM</th>
            <th style={{ padding: '0.75rem', textAlign: 'right' }}>ACTION</th>
          </tr>
        </thead>
        <tbody>
          {waitingPatients.map((p, idx) => (
            <tr key={p.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '0.75rem' }}>
                <strong className="mono">#{p.token_number}</strong>
                {idx === 0 && <span className="mono" style={{ marginLeft: '6px', fontSize: '0.65rem', background: '#f4f4f5', padding: '2px 5px', borderRadius: '4px' }}>NEXT</span>}
              </td>
              <td style={{ padding: '0.75rem', fontWeight: 600 }}>{p.patient_name}</td>
              <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>{p.age}y / {p.gender}</td>
              <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{p.note || '—'}</td>
              <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                <button
                  disabled={loading}
                  onClick={() => onCall(p.id)}
                  className="mono"
                  style={{
                    padding: '0.35rem 0.75rem',
                    background: '#ffffff',
                    border: '1px solid var(--border-light)',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    cursor: 'pointer'
                  }}
                >
                  Call Now
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
