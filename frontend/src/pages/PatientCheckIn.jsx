import React, { useState, useEffect } from 'react';
import { fetchClinicInfo, registerPatient } from '../services/api';

export default function PatientCheckIn({ slug, onJoined }) {
  const [clinic, setClinic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');
  const [note, setNote] = useState('');

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await fetchClinicInfo(slug);
        setClinic(data);
      } catch (err) {
        setError(err.message || 'Clinic record unavailable');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return alert('Full name required');
    if (!age || isNaN(age)) return alert('Valid age required');
    try {
      setSubmitting(true);
      const ticket = await registerPatient(slug, {
        patient_name: name.trim(),
        age: parseInt(age),
        gender,
        note: note.trim() || undefined,
      });
      localStorage.setItem('last_ticket_id', ticket.id);
      if (onJoined) onJoined(ticket.id);
    } catch (err) {
      setError(err.message || 'Check-in failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="mono" style={{ textAlign: 'center', padding: '5rem' }}>LOADING INTAKE MODULE...</div>;

  return (
    <div style={{ maxWidth: '540px', margin: '1rem auto' }}>
      <div className="flow-card" style={{ marginBottom: '1.25rem' }}>
        <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>PATIENT INTAKE COUNTER</div>
        <h1 className="serif" style={{ fontSize: '1.8rem', margin: '0.25rem 0' }}>{clinic?.name || 'Kronos Clinical'}</h1>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Dr. Eleanor Vance, MD • Suite 402 Cardiopulmonary</p>
      </div>

      <div className="flow-card">
        <h2 className="serif" style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Patient Registration</h2>
        {error && <div className="mono" style={{ color: '#dc2626', fontSize: '0.8rem', marginBottom: '1rem' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label className="mono" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '4px' }}>FULL NAME</label>
            <input
              type="text"
              required
              placeholder="e.g. Julian Sterling"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border-light)', borderRadius: '6px' }}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label className="mono" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '4px' }}>AGE</label>
              <input
                type="number"
                required
                min="0"
                max="125"
                placeholder="Years"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border-light)', borderRadius: '6px' }}
              />
            </div>
            <div>
              <label className="mono" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '4px' }}>GENDER</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border-light)', borderRadius: '6px', background: '#fff' }}
              >
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>
          <div style={{ marginBottom: '1.25rem' }}>
            <label className="mono" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '4px' }}>REASON / SYMPTOM (OPTIONAL)</label>
            <input
              type="text"
              placeholder="e.g. Routine follow-up, vitals check"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border-light)', borderRadius: '6px' }}
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="mono"
            style={{
              width: '100%',
              padding: '0.85rem',
              background: '#18181b',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            {submitting ? 'GENERATING TOKEN...' : 'GET CLINICAL TOKEN →'}
          </button>
        </form>
      </div>
    </div>
  );
}
