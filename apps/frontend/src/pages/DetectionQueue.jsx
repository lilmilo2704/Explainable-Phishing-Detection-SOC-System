import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchEmails } from '../api';
import { ConfidenceBadge, DataTable, ErrorState, FilterBar, LoadingState, PageHeader, Panel, RiskBadge, SectionHeader, StatusBadge } from '../components/ui';
import { VuiBox, VuiInput } from '../components/vision';

const DetectionQueue = () => {
  const [emails, setEmails] = useState([]);
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
      } catch {
        setError('Unable to load detection queue. Retry.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
    const timer = setInterval(loadData, 15000);
    return () => clearInterval(timer);
  }, []);

  const filtered = useMemo(() => {
    return emails
      .filter((e) => {
        const hit = `${e.subject || ''} ${e.sender || ''}`.toLowerCase().includes(search.toLowerCase());
        const riskOk = risk === 'all' ? true : (e.risk_level || '').toLowerCase() === risk;
        const statusValue = (e.review_status || e.quarantine_status || '').toLowerCase();
        const statusOk = status === 'all' ? true : statusValue.includes(status);
        return hit && riskOk && statusOk;
      })
      .sort((a, b) => new Date(b.received_at || 0).getTime() - new Date(a.received_at || 0).getTime());
  }, [emails, search, risk, status]);

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading detection queue..." /></VuiBox>;
  if (error) return <VuiBox className="page-content"><ErrorState message={error} /></VuiBox>;

  return (
    <VuiBox className="page-content">
      <PageHeader title="Detection Queue" description="Triage scored messages, evidence summaries, and current analyst review status." />
      <Panel>
        <SectionHeader title="Review Queue" subtitle="Filtered list of phishing detections and analyst review cases" />
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
          emptyText="No detections match the current filters."
          columns={[
            { key: 'select', label: '', render: () => <input type="checkbox" aria-label="Select case" onClick={(event) => event.stopPropagation()} /> },
            { key: 'case_id', label: 'Case ID', render: (r) => `CASE-${String(r.id || '').toUpperCase()}` },
            { key: 'received_at', label: 'Received Time', render: (r) => r.received_at ? new Date(r.received_at).toLocaleString() : 'N/A' },
            { key: 'sender', label: 'Sender' },
            { key: 'subject', label: 'Subject' },
            { key: 'prediction', label: 'Prediction', render: (r) => <StatusBadge status={r.prediction} /> },
            { key: 'confidence', label: 'Confidence', render: (r) => <ConfidenceBadge confidence={r.confidence} /> },
            { key: 'risk_level', label: 'Risk Level', render: (r) => <RiskBadge risk={r.risk_level} /> },
            { key: 'review_status', label: 'Review Status', render: (r) => <StatusBadge status={r.review_status || 'pending_review'} /> },
            { key: 'action', label: 'Action Taken', render: (r) => <StatusBadge status={r.quarantine_status || 'none'} /> },
            { key: 'analyst', label: 'Assigned Analyst', render: () => 'Unassigned' },
            { key: 'explanation', label: 'Top Explanation Factors', render: (r) => r.explanation_summary || 'Reply-to mismatch, suspicious domain' },
          ]}
        />
      </Panel>
    </VuiBox>
  );
};

export default DetectionQueue;
