import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchEmailDetail, quarantineEmail, releaseEmail, submitFeedback, reviewFeedback } from '../api';
import LocalExplanationPanel from '../components/LocalExplanationPanel';
import { ActionButton, ErrorState, LoadingState, PageHeader, Panel, RiskBadge, SectionHeader, StatusBadge, StatusBanner } from '../components/ui';
import { VuiBox } from '../components/vision';

const EmailInvestigation = () => {
  const { id } = useParams();
  const [email, setEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [explanationState, setExplanationState] = useState({ emailId: null, status: 'loading', data: null });

  useEffect(() => {
    const run = async () => {
      if (!id) { setEmail(null); setLoading(false); return; }
      try { setEmail(await fetchEmailDetail(id)); } finally { setLoading(false); }
    };
    run();
  }, [id]);

  const refresh = async () => setEmail(await fetchEmailDetail(email.id));

  const handleExplanationStateChange = useCallback((nextState) => {
    setExplanationState({ emailId: id, ...nextState });
  }, [id]);

  const submitAndReview = async (analystLabel, reasonCategory) => {
    if (!email) return;
    setBusy(true); setMsg('');
    try {
      const created = await submitFeedback(email.id, {
        feedback_type: 'wrong_detection',
        user_comment: `Analyst review from investigation: ${reasonCategory}`,
        submitted_by: 'soc_analyst',
      });
      await reviewFeedback(created.feedback_id, {
        analyst_label: analystLabel,
        error_type: null,
        reason_category: reasonCategory,
        review_status: 'confirmed',
        added_to_improvement_dataset: false,
        actor: 'analyst',
      });
      setMsg(
        analystLabel === 'phishing'
          ? 'Phishing classification confirmed. Use Move to Quarantine if containment is permitted for this mailbox.'
          : 'Legitimate classification confirmed. Use Release from Quarantine if a contained message should be restored.',
      );
      await refresh();
    } catch {
      setMsg('Action failed. Please retry.');
    } finally { setBusy(false); }
  };

  const handleRelease = async () => {
    if (!email) return;
    setBusy(true); setMsg('');
    try { await releaseEmail(email.id); setMsg('Email released from quarantine.'); await refresh(); }
    catch { setMsg('Release failed. Please retry.'); }
    finally { setBusy(false); }
  };

  const handleQuarantine = async () => {
    if (!email) return;
    setBusy(true); setMsg('');
    try { await quarantineEmail(email.id); setMsg('Email moved to quarantine.'); await refresh(); }
    catch { setMsg('Quarantine action failed. Please retry.'); }
    finally { setBusy(false); }
  };

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading investigation case..." /></VuiBox>;
  if (!id) return <VuiBox className="page-content"><ErrorState message="No case selected. Open a case from Detection Queue." /></VuiBox>;
  if (!email) return <VuiBox className="page-content"><ErrorState message="Unable to load investigation case." /></VuiBox>;

  const pd = email.prediction_details || {};
  const activeExplanationState = explanationState.emailId === email.id
    ? explanationState
    : { status: 'loading', data: null };
  const snapshotDisplay = activeExplanationState.status === 'loading'
    ? 'Loading...'
    : activeExplanationState.status === 'unavailable'
      ? 'Unavailable'
      : activeExplanationState.data?.snapshot_id || 'Not captured';

  return (
    <VuiBox className="page-content">
      <PageHeader title="Email Investigation" description="Review model evidence and take a reversible analyst action." right={<StatusBadge status={email.review_status || 'pending_review'} />} />
      {pd.trusted_prediction === false ? (
        <StatusBanner tone="warning" title="Analyst review required">
          The current model pipeline is not validated for trusted automatic decisions. Treat this result as shadow-mode review evidence only.
        </StatusBanner>
      ) : null}
      <VuiBox className="investigation-layout">
        <VuiBox style={{ display: 'grid', gap: 16 }}>
          <Panel>
            <SectionHeader title={`Case ${`CASE-${String(email.id || '').toUpperCase()}`}`} subtitle="Email metadata and detection context" />
            <div className="detail-grid">
              <span style={{ color: 'var(--text-2)' }}>Subject</span><span>{email.subject}</span>
              <span style={{ color: 'var(--text-2)' }}>Sender</span><span>{email.sender}</span>
              <span style={{ color: 'var(--text-2)' }}>Reply-To</span><span>{email.reply_to || 'N/A'}</span>
              <span style={{ color: 'var(--text-2)' }}>Recipient</span><span>{email.recipient}</span>
              <span style={{ color: 'var(--text-2)' }}>Received Time</span><span>{email.received_at ? new Date(email.received_at).toLocaleString() : 'N/A'}</span>
              <span style={{ color: 'var(--text-2)' }}>Model Version</span><span>{pd.model_version || pd.teacher_model_id || 'Unavailable'}</span>
              <span style={{ color: 'var(--text-2)' }}>Explanation Snapshot</span><span>{snapshotDisplay}</span>
              <span style={{ color: 'var(--text-2)' }}>Assigned Analyst</span><span>Unassigned</span>
            </div>
          </Panel>

          <Panel>
            <SectionHeader title="Local Explanation" subtitle="Human-readable explanation and feature evidence" />
            <LocalExplanationPanel key={email.id} emailId={email.id} onExplanationStateChange={handleExplanationStateChange} />
          </Panel>
        </VuiBox>

        <VuiBox style={{ display: 'grid', gap: 16 }}>
          <Panel>
            <SectionHeader title="Model Decision" />
            <div style={{ display: 'grid', gap: 10, fontSize: 13 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-2)' }}>Prediction</span><StatusBadge status={pd.prediction} /></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-2)' }}>Confidence</span><span>{pd.confidence != null ? `${(pd.confidence * 100).toFixed(1)}%` : 'N/A'}</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-2)' }}>Risk Level</span><RiskBadge risk={pd.risk_level} /></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-2)' }}>Quarantine Status</span><StatusBadge status={email.quarantine_status || 'none'} /></div>
            </div>
          </Panel>

          <Panel>
            <SectionHeader title="Analyst Actions" subtitle="Feedback supports future offline model improvement after analyst confirmation" />
            <div className="analyst-actions-grid">
              <ActionButton variant="danger" disabled={busy} onClick={() => submitAndReview('phishing', 'confirmed_malicious')}>Confirm Phishing</ActionButton>
              <ActionButton variant="warning" disabled={busy} onClick={() => submitAndReview('legitimate', 'analyst_confirmed_legitimate')}>Confirm Legitimate</ActionButton>
              <ActionButton variant="primary" disabled={busy} onClick={handleQuarantine}>Move to Quarantine</ActionButton>
              <ActionButton variant="success" disabled={busy} onClick={handleRelease}>Release from Quarantine</ActionButton>
              {msg ? <div style={{ fontSize: 12, color: 'var(--text-2)' }}>{msg}</div> : null}
            </div>
          </Panel>
        </VuiBox>
      </VuiBox>
    </VuiBox>
  );
};

export default EmailInvestigation;
