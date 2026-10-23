import React from 'react';

function getOrdinal(n) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

export default function QueueFlowLine({ ticket }) {
  const aheadCount = ticket.position_ahead || 0;
  const userToken = ticket.token_number;
  const nowServing = ticket.currently_serving_token || (userToken > aheadCount ? userToken - aheadCount - 1 : 1);

  // Generate intermediate queue nodes ahead of user (up to 2 visible to match design)
  const intermediateNodes = [];
  for (let i = aheadCount; i >= 1; i--) {
    const tokenNum = userToken - (aheadCount - i + 1);
    intermediateNodes.push({
      token: tokenNum > 0 ? tokenNum : `A-${i}`,
      label: i === 1 ? 'Next in Line' : 'In Line Ahead',
      sublabel: `${getOrdinal(i)} in Line`,
    });
  }

  return (
    <div className="flow-card">
      {/* Header & Legend */}
      <div className="flow-top-meta">
        <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          LEFT-TO-RIGHT QUEUE PROGRESSION ●
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="flow-meta-pill mono">
            ⚡ Avg. Velocity: {ticket.avg_consultation_time_mins || 8.5} min/patient
          </span>
          <div className="flow-legend mono">
            <span>● You</span>
            <span>○ Waiting Ahead</span>
            <span>● Target Doctor</span>
          </div>
        </div>
      </div>

      <h2 className="serif" style={{ fontSize: '1.65rem', fontWeight: 500, margin: '0.2rem 0' }}>
        Patient Line Flow
      </h2>
      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
        Flow of waiting patients progressing towards the consultation cabin at the far right.
      </p>

      {/* Callout Info Strip */}
      <div className="flow-callout-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div className="ahead-badge-box mono">
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{aheadCount}</div>
            <div style={{ fontSize: '0.55rem', color: 'var(--text-muted)' }}>AHEAD</div>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>
              {aheadCount === 0 ? 'Your turn has arrived!' : `${aheadCount} Patients Ahead in Queue`}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Waiting line is moving smoothly toward Cabin 4B. Estimated wait is ~{ticket.estimated_wait_mins} minutes.
            </div>
          </div>
        </div>
        <div className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          → Direction: Toward Dr. Vance (Right)
        </div>
      </div>

      {/* Horizontal Line Track */}
      <div className="track-wrapper">
        <div className="track-line">
          {/* User Node */}
          <div className="track-node">
            <span className="node-badge-tag tag-user mono">YOUR POSITION</span>
            <div className="node-circle active-user">👤</div>
            <div className="node-card">
              <div className="mono" style={{ fontWeight: 700, fontSize: '0.85rem' }}>Token #{userToken}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{ticket.patient_name}</div>
              <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {aheadCount === 0 ? 'Serving Now' : `${getOrdinal(aheadCount + 1)} in Line`}
              </div>
            </div>
          </div>

          {/* Intermediary Nodes */}
          {intermediateNodes.slice(0, 3).map((node, idx) => (
            <React.Fragment key={idx}>
              <div className="track-arrow">→</div>
              <div className="track-node">
                <div className="node-circle">👤</div>
                <div className="node-card">
                  <div className="mono" style={{ fontWeight: 700, fontSize: '0.85rem' }}>Token #{node.token}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{node.label}</div>
                  <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{node.sublabel}</div>
                </div>
              </div>
            </React.Fragment>
          ))}

          <div className="track-arrow">→</div>

          {/* Destination Node */}
          <div className="track-node">
            <span className="node-badge-tag tag-destination mono">DESTINATION</span>
            <div className="node-circle destination">🚪</div>
            <div className="node-card">
              <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>{ticket.doctor_name || 'Dr. Eleanor Vance'}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Cabin 4B</div>
              <div className="mono" style={{ fontSize: '0.7rem', fontWeight: 600 }}>Now: Token #{nowServing}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Turnaround Bottom Bar */}
      <div className="turnaround-bar mono">
        <div>
          <span style={{ fontWeight: 600 }}>2 Consultations immediately precede you</span>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Patients have completed triage and prelim vitals checks.
          </div>
        </div>
        <div style={{ textAlign: 'right', fontSize: '0.75rem' }}>
          <div>Room Turnaround <strong>Fast (92%)</strong></div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: '92%' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
