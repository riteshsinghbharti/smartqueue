import React, { useState, useEffect } from 'react';

export default function ClinicalHeader({ doctorName = 'Dr. Eleanor Vance, MD', onRefresh }) {
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-US', { hour12: false }) + ' EDT');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header>
      {/* Top Bar */}
      <div className="header-top-bar mono">
        <div>KRONOS CLINICAL / PATIENT CHECK-IN</div>
        <div>WING 4 • CABIN 4B • {currentTime}</div>
      </div>

      {/* Sub Bar */}
      <div className="header-sub-bar mono">
        <div>
          SESSION #MED-8492 / APT-2024-90412 / {doctorName.toUpperCase()} • CARDIOPULMONARY
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <span>● LIVE QUEUE FEED</span>
          <button
            onClick={onRefresh}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              fontSize: '0.72rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '3px'
            }}
          >
            🔄 Refresh
          </button>
        </div>
      </div>
    </header>
  );
}
