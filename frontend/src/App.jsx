import React, { useState, useEffect } from 'react';
import ClinicalHeader from './components/ClinicalHeader';
import ClinicalFooter from './components/ClinicalFooter';
import PatientLiveTicket from './pages/PatientLiveTicket';
import PatientCheckIn from './pages/PatientCheckIn';
import ClinicAdmin from './pages/ClinicAdmin';

export default function App() {
  const [route, setRoute] = useState(resolveRoute());

  function resolveRoute() {
    const path = window.location.pathname;
    const ticketMatch = path.match(/^\/ticket\/([^\/]+)/);
    if (ticketMatch) return { page: 'ticket', ticketId: ticketMatch[1] };

    const qMatch = path.match(/^\/q\/([^\/]+)/);
    if (qMatch) return { page: 'checkin', slug: qMatch[1] };

    const adminMatch = path.match(/^\/admin\/([^\/]+)/);
    if (adminMatch) return { page: 'admin', slug: adminMatch[1] };

    // Default to demo ticket or checkin
    const savedTicket = localStorage.getItem('last_ticket_id');
    if (savedTicket) return { page: 'ticket', ticketId: savedTicket };

    return { page: 'checkin', slug: 'apex-clinic' };
  }

  useEffect(() => {
    const onPop = () => setRoute(resolveRoute());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const navigate = (url) => {
    window.history.pushState({}, '', url);
    setRoute(resolveRoute());
  };

  return (
    <div className="clinical-app">
      <ClinicalHeader
        doctorName="Dr. Eleanor Vance, MD"
        onRefresh={() => window.location.reload()}
      />

      <main className="clinical-container">
        {route.page === 'ticket' && (
          <PatientLiveTicket
            ticketId={route.ticketId}
            onExit={() => navigate('/q/apex-clinic')}
          />
        )}

        {route.page === 'checkin' && (
          <PatientCheckIn
            slug={route.slug}
            onJoined={(id) => navigate(`/ticket/${id}`)}
          />
        )}

        {route.page === 'admin' && (
          <ClinicAdmin slug={route.slug} />
        )}
      </main>

      <ClinicalFooter />
    </div>
  );
}
