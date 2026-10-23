// API client for Smart Virtual Queue
const BASE_URL = import.meta.env.VITE_API_BASE_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');

export async function fetchClinicInfo(slug) {
  const res = await fetch(`${BASE_URL}/api/queues/${slug}/info`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to load clinic information');
  }
  return res.json();
}

export async function registerPatient(slug, data) {
  const res = await fetch(`${BASE_URL}/api/queues/${slug}/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Could not join queue');
  }
  return res.json();
}

export async function fetchTicketStatus(ticketId) {
  const res = await fetch(`${BASE_URL}/api/tickets/${ticketId}/status`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch ticket status');
  }
  return res.json();
}

export async function fetchAdminDashboard(slug) {
  const res = await fetch(`${BASE_URL}/api/queues/${slug}/admin`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to load admin dashboard');
  }
  return res.json();
}

export async function callNextPatient(slug) {
  const res = await fetch(`${BASE_URL}/api/queues/${slug}/call-next`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to advance queue');
  }
  return res.json();
}

export async function updateTicketStatus(ticketId, status) {
  const res = await fetch(`${BASE_URL}/api/tickets/${ticketId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update ticket status');
  }
  return res.json();
}

export function getQrCodeImageUrl(slug) {
  return `${BASE_URL}/api/queues/${slug}/qr`;
}
