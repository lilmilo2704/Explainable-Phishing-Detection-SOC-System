const API_URL = 'http://127.0.0.1:8000';

export const fetchSummary = async () => {
  const response = await fetch(`${API_URL}/dashboard/summary`);
  if (!response.ok) throw new Error('Failed to fetch summary');
  return response.json();
};

export const fetchEmails = async () => {
  const response = await fetch(`${API_URL}/emails`);
  if (!response.ok) throw new Error('Failed to fetch emails');
  return response.json();
};

export const fetchEmailDetail = async (id) => {
  const response = await fetch(`${API_URL}/emails/${id}`);
  if (!response.ok) throw new Error('Failed to fetch email details');
  return response.json();
};

export const fetchLocalExplanation = async (id) => {
  const response = await fetch(`${API_URL}/emails/${id}/local-explanation`);
  if (!response.ok) throw new Error('Failed to fetch local explanation');
  return response.json();
};

export const fetchGlobalExplanation = async () => {
  const response = await fetch(`${API_URL}/global-explanation`);
  if (!response.ok) throw new Error('Failed to fetch global explanation');
  return response.json();
};

export const fetchFeedback = async () => {
  const response = await fetch(`${API_URL}/feedback`);
  if (!response.ok) throw new Error('Failed to fetch feedback cases');
  return response.json();
};

export const fetchModelHealth = async () => {
  const response = await fetch(`${API_URL}/monitoring/model-health`);
  if (!response.ok) throw new Error('Failed to fetch model health');
  return response.json();
};

export const exportConfirmedFeedback = async () => {
  const response = await fetch(`${API_URL}/feedback/export-confirmed`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to export confirmed feedback');
  return response.json();
};

export const submitFeedback = async (id, payload) => {
  const response = await fetch(`${API_URL}/emails/${id}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to submit feedback');
  return response.json();
};

export const reviewFeedback = async (id, payload) => {
  const response = await fetch(`${API_URL}/feedback/${id}/review`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to review feedback');
  return response.json();
};

export const quarantineEmail = async (id, provider = 'mock') => {
  const response = await fetch(`${API_URL}/emails/${id}/quarantine`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider }),
  });
  if (!response.ok) throw new Error('Failed to quarantine email');
  return response.json();
};

export const releaseEmail = async (id, provider = 'mock') => {
  const response = await fetch(`${API_URL}/emails/${id}/release`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider }),
  });
  if (!response.ok) throw new Error('Failed to release email');
  return response.json();
};

export const fetchModelRegistry = async () => {
  const response = await fetch(`${API_URL}/api/models`);
  if (!response.ok) throw new Error('Failed to fetch model registry');
  return response.json();
};

export const fetchActiveModelConfig = async () => {
  const response = await fetch(`${API_URL}/api/models/active`);
  if (!response.ok) throw new Error('Failed to fetch active model config');
  return response.json();
};

export const saveActiveModelConfig = async (payload) => {
  const response = await fetch(`${API_URL}/api/models/active`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err?.detail || 'Failed to save model config');
  }
  return response.json();
};

export const syncMailbox = async (payload = { provider: 'gmail', limit: 200 }) => {
  const response = await fetch(`${API_URL}/mailbox/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err?.detail || 'Failed to sync mailbox');
  }
  return response.json();
};
