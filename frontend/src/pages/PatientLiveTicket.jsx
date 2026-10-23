import React, { useState, useEffect } from 'react';
import { fetchTicketStatus } from '../services/api';
import MetricCards from '../components/MetricCards';
import QueueFlowLine from '../components/QueueFlowLine';

export default function PatientLiveTicket({ ticketId, onExit }) {
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadTicket = async (isFirst = false) => {
    try {
      if (isFirst) setLoading(true);
      const data = await fetchTicketStatus(ticketId);
      setTicket(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Unable to sync with queue');
    } finally {
      if (isFirst) setLoading(false);
    }
  };

  useEffect(() => {
    loadTicket(true);
    const interval = setInterval(() => {
      if (!document.hidden && ticket?.status !== 'completed') {
        loadTicket(false);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [ticketId]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '6rem 1rem' }} className="mono">
        <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>SYNCING KRONOS FEED...</div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Retrieving live token velocity</div>
      </div>
    );
  }

  if (error && !ticket) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <h2 className="serif" style={{ marginBottom: '1rem' }}>Ticket Record Unavailable</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error}</p>
        <button onClick={onExit} style={{ padding: '0.6rem 1.25rem', border: '1px solid #000', background: '#fff', cursor: 'pointer' }}>
          Return to Check-in
        </button>
      </div>
    );
  }

  const nowServing = ticket.currently_serving_token || 23;

  return (
    <div style={{ animation: 'fadeIn 0.3s ease' }}>
      {/* Hero Section */}
      <div className="hero-row">
        <div>
          <div className="token-indicator mono">
            <span>YOUR TOKEN: #{ticket.token_number}</span>
            <span className="pill-in-clinic">In Clinic</span>
          </div>
          <h1 className="hero-title serif">Consultation Queue & Token Velocity</h1>
          <p className="hero-desc">
            Real-time patient throughput for Suite 402. Updates dynamically as consultations conclude.
          </p>
        </div>

        {/* Top-Right Now Consulting Box */}
        <div className="now-consulting-box">
          <div className="consulting-icon-circle">🩺</div>
          <div>
            <div className="mono" style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>NOW CONSULTING</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>Token #{nowServing}</div>
          </div>
          <span className="badge-elapsed mono">● 11m elapsed</span>
        </div>
      </div>

      {/* 3-Card Metrics Section */}
      <MetricCards ticket={ticket} />

      {/* Main Flow Card */}
      <QueueFlowLine ticket={ticket} />

      {/* Actions */}
      <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
        <button
          onClick={onExit}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            textDecoration: 'underline'
          }}
          className="mono"
        >
          ← Return to Intake Counter
        </button>
      </div>
    </div>
  );
}
