import React, { useState, useEffect } from 'react';
import { fetchAdminDashboard, callNextPatient, updateTicketStatus, getQrCodeImageUrl } from '../services/api';
import AdminQueueTable from '../components/AdminQueueTable';

export default function ClinicAdmin({ slug }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showQr, setShowQr] = useState(false);

  const load = async (first = false) => {
    try {
      if (first) setLoading(true);
      const res = await fetchAdminDashboard(slug);
      setData(res);
    } catch (e) {
      // Handled silently for polling
    } finally {
      if (first) setLoading(false);
    }
  };

  useEffect(() => {
    load(true);
    const interval = setInterval(() => { if (!document.hidden) load(false); }, 6000);
    return () => clearInterval(interval);
  }, [slug]);

  const handleNext = async () => {
    try {
      setActionLoading(true);
      await callNextPatient(slug);
      await load(false);
    } catch (e) {
      alert(e.message || 'Error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStatus = async (id, status) => {
    try {
      setActionLoading(true);
      await updateTicketStatus(id, status);
      await load(false);
    } catch (e) {
      alert(e.message || 'Error');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="mono" style={{ textAlign: 'center', padding: '5rem' }}>LOADING CONSOLE...</div>;
  if (!data) return <div className="mono" style={{ textAlign: 'center', padding: '5rem' }}>ERROR LOADING CLINIC</div>;

  const { clinic, currently_serving, waiting_patients, stats } = data;

  return (
    <div>
      {/* Console Header */}
      <div className="flow-card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>CLINICAL SUPERVISOR CONSOLE</div>
            <h1 className="serif" style={{ fontSize: '1.8rem', margin: '0.2rem 0' }}>{clinic.name}</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{clinic.doctor_name} • Cabin 4B</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button onClick={() => setShowQr(true)} className="mono" style={{ padding: '0.6rem 1rem', background: '#fff', border: '1px solid var(--border-light)', borderRadius: '6px', cursor: 'pointer' }}>
              📱 QR Code
            </button>
            <button
              onClick={handleNext}
              disabled={actionLoading || waiting_patients.length === 0}
              className="mono"
              style={{ padding: '0.6rem 1.25rem', background: '#18181b', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
            >
              📢 Call Next Patient
            </button>
          </div>
        </div>
      </div>

      {/* Currently Serving Banner */}
      <div className="flow-card" style={{ marginBottom: '1.25rem' }}>
        <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>CABIN OCCUPANCY</div>
        {currently_serving ? (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span className="mono" style={{ fontSize: '1.5rem', fontWeight: 700, marginRight: '0.75rem' }}>
                Token #{currently_serving.token_number}
              </span>
              <span style={{ fontSize: '1.1rem', fontWeight: 600 }}>{currently_serving.patient_name}</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginLeft: '0.5rem' }}>
                ({currently_serving.age}y / {currently_serving.gender})
              </span>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={() => handleStatus(currently_serving.id, 'completed')} className="mono" style={{ padding: '0.5rem 1rem', background: '#18181b', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                ✅ Mark Done
              </button>
              <button onClick={() => handleStatus(currently_serving.id, 'no_show')} className="mono" style={{ padding: '0.5rem 1rem', background: '#fff', border: '1px solid var(--border-light)', borderRadius: '4px', cursor: 'pointer' }}>
                No Show
              </button>
            </div>
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Cabin is vacant. Click "Call Next Patient" to admit next in queue.</div>
        )}
      </div>

      {/* Waiting Table */}
      <div className="flow-card">
        <div className="mono" style={{ fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem' }}>
          WAITING QUEUE ({waiting_patients.length})
        </div>
        <AdminQueueTable waitingPatients={waiting_patients} onCall={(id) => handleStatus(id, 'called')} loading={actionLoading} />
      </div>

      {/* QR Modal */}
      {showQr && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
          <div className="flow-card" style={{ maxWidth: '380px', textAlign: 'center', padding: '2rem' }}>
            <h3 className="serif" style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>Counter Check-in QR</h3>
            <img src={getQrCodeImageUrl(slug)} alt="QR" style={{ width: '200px', height: '200px', margin: '1rem auto', display: 'block' }} />
            <button onClick={() => setShowQr(false)} className="mono" style={{ padding: '0.5rem 1.5rem', background: '#18181b', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
