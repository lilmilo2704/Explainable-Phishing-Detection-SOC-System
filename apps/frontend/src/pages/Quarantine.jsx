import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchEmails, releaseEmail } from '../api';
import { ActionButton, DataTable, ErrorState, LoadingState, PageHeader, Panel, RiskBadge, SectionHeader, StatusBadge } from '../components/ui';
import { VuiBox } from '../components/vision';

const Quarantine = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busyId, setBusyId] = useState('');
  const navigate = useNavigate();

  const load = async () => {
    const data = await fetchEmails();
    setEmails(data.items || []);
  };

  useEffect(() => {
    const boot = async () => {
      try { await load(); } catch { setError('Unable to load quarantine data. Retry.'); } finally { setLoading(false); }
    };
    boot();
    window.addEventListener('phishguard:mailbox-synced', load);
    return () => window.removeEventListener('phishguard:mailbox-synced', load);
  }, []);

  const quarantined = useMemo(() => emails.filter((e) => e.quarantine_status === 'quarantined'), [emails]);

  const handleRelease = async (id) => {
    setBusyId(id);
    try { await releaseEmail(id); await load(); } finally { setBusyId(''); }
  };

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading quarantine queue..." /></VuiBox>;
  if (error) return <VuiBox className="page-content"><ErrorState message={error} /></VuiBox>;

  return (
    <VuiBox className="page-content">
      <PageHeader title="Quarantine" description="Review contained messages before confirmation or release. Quarantine is reversible." />
      <Panel>
        <SectionHeader title="Quarantine Review Queue" subtitle={`${quarantined.length} emails currently quarantined`} />
        <DataTable
          rows={quarantined}
          emptyText="No quarantined emails found."
          columns={[
            { key: 'case_id', label: 'Case ID', render: (r) => `CASE-${String(r.id || '').toUpperCase()}` },
            { key: 'received_at', label: 'Received Time', render: (r) => r.received_at ? new Date(r.received_at).toLocaleString() : 'N/A' },
            { key: 'subject', label: 'Subject', render: (r) => <span onClick={() => navigate(`/investigation/${r.id}`)} style={{ cursor: 'pointer', textDecoration: 'underline' }}>{r.subject}</span> },
            { key: 'sender', label: 'Sender' },
            { key: 'risk_level', label: 'Risk', render: (r) => <RiskBadge risk={r.risk_level} /> },
            { key: 'review_status', label: 'Review Status', render: (r) => <StatusBadge status={r.review_status || 'pending_review'} /> },
            { key: 'analyst', label: 'Assigned Analyst', render: () => 'Unassigned' },
            { key: 'action', label: 'Action', render: (r) => <ActionButton variant="success" disabled={busyId === r.id} onClick={() => handleRelease(r.id)}>{busyId === r.id ? 'Releasing...' : 'Release'}</ActionButton> },
          ]}
        />
      </Panel>
    </VuiBox>
  );
};

export default Quarantine;
