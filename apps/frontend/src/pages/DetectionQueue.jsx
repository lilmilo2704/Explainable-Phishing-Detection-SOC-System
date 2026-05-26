import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchEmails } from '../api';
import { ConfidenceBadge, DataTable, ErrorState, FilterBar, LoadingState, PageHeader, Panel, RiskBadge, SectionHeader, StatusBadge } from '../components/ui';
import { VuiBox, VuiInput } from '../components/vision';

const providerLabel = (source) => {
  if (source === 'mock') return 'Mock fixture mailbox';
  if (source === 'gmail') return 'Gmail mailbox';
  return source ? `${source.replaceAll('_', ' ')} mailbox` : 'Configured mailbox';
};

const resultBadge = (email) => {
  if (email.model_error || email.pipeline_status === 'model_error' || email.prediction_status === 'model_error') {
    return (
      <div>
        <StatusBadge status="model_error" />
        <div className="subtle-text">No trusted prediction; investigate manually.</div>
      </div>
    );
  }
  if (email.trusted_prediction === false) {
    return (
      <div>
        <StatusBadge status={email.pipeline_status || 'needs_review'} />
        <div className="subtle-text">Untrusted result; analyst review required.</div>
      </div>
    );
  }
  return <StatusBadge status={email.prediction} />;
};

const DetectionQueue = () => {
  const [emails, setEmails] = useState([]);
  const [mailboxSource, setMailboxSource] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [risk, setRisk] = useState('all');
  const [status, setStatus] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchEmails();
        setEmails(data.items || []);
        setMailboxSource(data.mailbox_source || '');
      } catch {
        setError('Unable to load detection queue. Retry.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
    window.addEventListener('phishguard:mailbox-synced', loadData);
    return () => window.removeEventListener('phishguard:mailbox-synced', loadData);
  }, []);

  const filtered = useMemo(() => {
    return emails
      .filter((e) => {
        const hit = `${e.subject || ''} ${e.sender || ''}`.toLowerCase().includes(search.toLowerCase());
        const riskOk = risk === 'all' ? true : (e.risk_level || '').toLowerCase() === risk;
        const reviewStatus = (e.review_status || '').toLowerCase();
        const quarantineStatus = (e.quarantine_status || '').toLowerCase();
        const statusOk = status === 'all'
          || (['quarantined', 'released'].includes(status)
            ? quarantineStatus === status
            : status === 'review'
              ? reviewStatus.includes('review')
              : reviewStatus === status);
        return hit && riskOk && statusOk;
      })
      .sort((a, b) => new Date(b.received_at || 0).getTime() - new Date(a.received_at || 0).getTime());
  }, [emails, search, risk, status]);

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading detection queue..." /></VuiBox>;
  if (error) return <VuiBox className="page-content"><ErrorState message={error} /></VuiBox>;

  const mailboxLabel = providerLabel(mailboxSource);

  return (
    <VuiBox className="page-content">
      <PageHeader title="Detection Queue" description={`${mailboxLabel} messages scanned through the manually triggered mailbox workflow.`} />
      <Panel>
        <SectionHeader title={`${mailboxLabel} Review Queue`} subtitle="Filtered list of scan results and analyst review cases" />
        <FilterBar>
          <VuiInput value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search sender or subject" />
          <VuiInput component="select" value={risk} onChange={(e) => setRisk(e.target.value)}>
            <option value="all">All risk levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </VuiInput>
          <VuiInput component="select" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="all">All statuses</option>
            <option value="new">New</option>
            <option value="review">Review</option>
            <option value="quarantined">Quarantined</option>
            <option value="released">Released</option>
          </VuiInput>
        </FilterBar>

        <DataTable
          rows={filtered.slice(0, 100)}
          onRowClick={(row) => navigate(`/investigation/${row.id}`)}
          emptyText={emails.length === 0 ? `No messages from ${mailboxLabel.toLowerCase()} have been scanned yet. Use mailbox sync to load cases.` : 'No detections match the current filters.'}
          columns={[
            { key: 'select', label: '', render: () => <input type="checkbox" aria-label="Select case" onClick={(event) => event.stopPropagation()} /> },
            { key: 'case_id', label: 'Case ID', render: (r) => `CASE-${String(r.id || '').toUpperCase()}` },
            { key: 'received_at', label: 'Received Time', render: (r) => r.received_at ? new Date(r.received_at).toLocaleString() : 'N/A' },
            { key: 'sender', label: 'Sender' },
            { key: 'subject', label: 'Subject' },
            { key: 'prediction', label: 'Triage Result', render: resultBadge },
            { key: 'confidence', label: 'Confidence / Trust', render: (r) => r.trusted_prediction === false ? <StatusBadge status="needs_review" /> : <ConfidenceBadge confidence={r.confidence} /> },
            { key: 'risk_level', label: 'Risk Level', render: (r) => <RiskBadge risk={r.risk_level} /> },
            { key: 'review_status', label: 'Review Status', render: (r) => <StatusBadge status={r.review_status || 'pending_review'} /> },
            { key: 'action', label: 'Action Taken', render: (r) => <StatusBadge status={r.quarantine_status || 'none'} /> },
            { key: 'analyst', label: 'Assigned Analyst', render: () => 'Unassigned' },
            { key: 'explanation', label: 'Top Explanation Factors', render: (r) => r.explanation_summary || 'Open case for explanation details' },
          ]}
        />
      </Panel>
    </VuiBox>
  );
};

export default DetectionQueue;
