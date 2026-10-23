import React from 'react';

function getOrdinal(n) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

export default function MetricCards({ ticket }) {
  const position = (ticket.position_ahead || 0) + 1;
  const isNow = ticket.position_ahead === 0 || ticket.status === 'called';

  // Compute estimated call clock time
  const callDate = new Date(Date.now() + (ticket.estimated_wait_mins || 0) * 60000);
  const callTimeStr = callDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) + ' EDT';

  return (
    <section className="metrics-grid">
      {/* 1. Current Position */}
      <div className="metric-card">
        <div className="metric-header mono">
          <span>CURRENT POSITION</span>
          <span>≡</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number-serif serif">{isNow ? 'Now' : getOrdinal(position)}</span>
          <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>{isNow ? 'Serving' : 'in line'}</span>
        </div>
        <div className="metric-footer-strip mono">
          <span>{ticket.position_ahead} ahead of you</span>
          <span>100% On-Site</span>
        </div>
      </div>

      {/* 2. Estimated Call Time */}
      <div className="metric-card">
        <div className="metric-header mono">
          <span>ESTIMATED CALL TIME</span>
          <span>🕒</span>
        </div>
        <div className="metric-value-row">
          <span className="metric-number-mono mono">{isNow ? 'Immediate' : callTimeStr}</span>
        </div>
        <div className="metric-footer-strip mono">
          <span>{isNow ? 'Proceed to door' : `~${ticket.estimated_wait_mins}m remaining`}</span>
          <span>●</span>
        </div>
      </div>

      {/* 3. Doctor & Cabin */}
      <div className="metric-card">
        <div className="metric-header mono">
          <span>DOCTOR & CABIN</span>
          <span>🚪</span>
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)' }}>
            {ticket.doctor_name || 'Dr. Eleanor Vance'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Cabin 4B, Level 2 • Cardiopulmonary
          </div>
        </div>
        <div className="metric-footer-strip mono" style={{ marginTop: '0.9rem' }}>
          <span>Attending On-Schedule</span>
          <span>Suite 402</span>
        </div>
      </div>
    </section>
  );
}
