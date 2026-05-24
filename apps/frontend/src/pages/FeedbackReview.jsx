import { useEffect, useMemo, useState } from 'react';
import { fetchFeedback, reviewFeedback } from '../api';
import { ActionButton, DataTable, ErrorState, LoadingState, PageHeader, Panel, SectionHeader, StatusBadge } from '../components/ui';
import { VuiBox } from '../components/vision';

const FeedbackReview = () => {
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCase, setSelectedCase] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const data = await fetchFeedback();
    setFeedback(data || []);
    return data || [];
  };

  useEffect(() => {
    const loadData = async () => {
      try { await load(); } catch { setError('Unable to load feedback cases. Retry.'); } finally { setLoading(false); }
    };
    loadData();
    window.addEventListener('phishguard:mailbox-synced', load);
    return () => window.removeEventListener('phishguard:mailbox-synced', load);
  }, []);

  const pendingCount = useMemo(() => feedback.filter((f) => (f.review_status || 'pending') !== 'confirmed').length, [feedback]);

  const handleReview = async (label, reason = 'analyst_review') => {
    if (!selectedCase) return;
    setBusy(true);
    try {
      await reviewFeedback(selectedCase.id, {
        analyst_label: label,
        error_type: null,
        reason_category: reason,
        review_status: 'confirmed',
        added_to_improvement_dataset: false,
        actor: 'analyst',
      });
      const updated = await load();
      setSelectedCase(updated.find((f) => f.id === selectedCase.id) || null);
    } finally { setBusy(false); }
  };

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading feedback review queue..." /></VuiBox>;
  if (error) return <VuiBox className="page-content"><ErrorState message={error} /></VuiBox>;

  return (
    <VuiBox className="page-content">
      <PageHeader title="Feedback Review" description="Validate reported model mistakes before they enter any future offline improvement process." />
      <VuiBox className="grid-2">
        <Panel>
          <SectionHeader title="Feedback Cases" subtitle={`${pendingCount} pending review`} />
          <DataTable
            rows={feedback}
            selectedKey={selectedCase?.id}
            onRowClick={(row) => setSelectedCase(row)}
            emptyText="No feedback cases are pending review."
            columns={[
              { key: 'id', label: 'Case ID', render: (r) => `CASE-${String(r.id || '').toUpperCase()}` },
              { key: 'original_prediction', label: 'Original Prediction', render: (r) => <StatusBadge status={r.original_prediction} /> },
              { key: 'original_confidence', label: 'Original Confidence', render: (r) => r.original_confidence != null ? `${(r.original_confidence * 100).toFixed(0)}%` : 'N/A' },
              { key: 'error_type', label: 'Error Type', render: (r) => r.error_type || 'Pending Classification' },
              { key: 'review_status', label: 'Review Status', render: (r) => <StatusBadge status={r.review_status || 'pending_review'} /> },
              { key: 'created_at', label: 'Created', render: (r) => r.created_at ? new Date(r.created_at).toLocaleString() : 'N/A' },
            ]}
          />
        </Panel>

        <Panel>
          {selectedCase ? (
            <>
              <SectionHeader title={`Feedback Case ${selectedCase.id}`} subtitle="Analyst confirmation is required before future model improvement use" />
              <div style={{ display: 'grid', gap: 10, fontSize: 13, marginBottom: 12 }}>
                <div><strong>User Feedback:</strong> {selectedCase.user_feedback || 'No comment provided.'}</div>
                <div><strong>Analyst Label:</strong> {selectedCase.analyst_label || 'Pending'}</div>
                <div><strong>Reason Category:</strong> {selectedCase.reason_category || 'Unspecified'}</div>
                <div><strong>Explanation Snapshot:</strong> {`EXP-${String(selectedCase.email_id || selectedCase.id).toUpperCase()}`}</div>
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                <ActionButton variant="danger" disabled={busy} onClick={() => handleReview('phishing', 'confirmed_malicious')}>Confirm Phishing</ActionButton>
                <ActionButton variant="success" disabled={busy} onClick={() => handleReview('legitimate', 'false_positive')}>Confirm Legitimate</ActionButton>
                <div className="governance-note">Confirmed feedback updates live monitoring only. Retraining-data export and automatic retraining are disabled for this prototype.</div>
              </div>
            </>
          ) : (
            <ErrorState message="Select a feedback case to review details and actions." />
          )}
        </Panel>
      </VuiBox>
    </VuiBox>
  );
};

export default FeedbackReview;
