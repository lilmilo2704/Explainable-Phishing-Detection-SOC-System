import { useEffect, useState } from 'react';
import { Activity, Archive, ClipboardList, Mail, ShieldCheck, ShieldX } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ModelReadinessPanel from '../components/ModelReadinessPanel';
import { fetchModelHealth } from '../api';
import { ErrorState, LoadingState, PageHeader, Panel, SectionHeader, StatusBanner } from '../components/ui';
import { VuiBox } from '../components/vision';

const providerLabel = (source) => {
  if (source === 'mock') return 'mock fixture mailbox';
  if (source === 'gmail') return 'Gmail mailbox';
  return source ? `${source.replaceAll('_', ' ')} mailbox` : 'configured mailbox';
};

const ModelMonitoring = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try { setHealth(await fetchModelHealth()); }
      catch { setError('Unable to load model monitoring data. Retry.'); }
      finally { setLoading(false); }
    };
    loadData();
    window.addEventListener('phishguard:mailbox-synced', loadData);
    return () => window.removeEventListener('phishguard:mailbox-synced', loadData);
  }, []);

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading model monitoring..." /></VuiBox>;
  if (error || !health) return <VuiBox className="page-content"><ErrorState message={error || 'Unable to load model monitoring data. Retry.'} /></VuiBox>;

  const live = health.live_operational || health;
  const benchmark = health.research_benchmark || {};
  const mailboxLabel = providerLabel(health.mailbox_source);

  return (
    <VuiBox className="page-content">
      <PageHeader title="Model Monitoring" description={`Operational state for the ${mailboxLabel}, benchmark explanation fidelity, and analyst-confirmed validation state.`} />

      <Panel style={{ marginBottom: 16 }}>
        <SectionHeader title="Current Model Pair" subtitle={`Detector and surrogate applied to the ${mailboxLabel} workflow`} />
        <div className="summary-grid">
          <div>Detector: <strong>{health.model_name} ({health.model_version})</strong></div>
          <div>Surrogate: <strong>{health.surrogate_name} ({health.surrogate_version})</strong></div>
        </div>
      </Panel>

      <ModelReadinessPanel readiness={health.model_readiness} mailboxSource={health.mailbox_source} />

      <SectionHeader title="Operational Metrics" subtitle={`Calculated from locally stored ${mailboxLabel} workflow state`} />
      <StatusBanner tone="info" title="Operational validation status">{live.validation_message}</StatusBanner>
      <VuiBox className="grid-cards">
        <MetricCard title="Emails Scanned" value={live.total_scanned ?? 0} icon={<Mail size={18} />} />
        <MetricCard title="Quarantined" value={live.quarantine_count ?? 0} icon={<Archive size={18} />} color="var(--warning)" />
        <MetricCard title="Review Backlog" value={live.review_backlog ?? 0} icon={<ClipboardList size={18} />} />
        <MetricCard title="Model Errors" value={live.model_errors ?? 0} icon={<Activity size={18} />} color="var(--danger)" />
        <MetricCard title="Confirmed False Positives" value={live.false_positives ?? 0} icon={<ShieldCheck size={18} />} color="var(--warning)" />
        <MetricCard title="Confirmed False Negatives" value={live.false_negatives ?? 0} icon={<ShieldX size={18} />} color="var(--danger)" />
        <MetricCard title="Pending Feedback" value={live.pending_feedback ?? 0} icon={<Activity size={18} />} />
        <MetricCard title="Confirmed Feedback" value={live.confirmed_feedback ?? 0} icon={<ShieldCheck size={18} />} />
      </VuiBox>

      <SectionHeader title="Research Benchmark Metrics" subtitle={`Fixed surrogate fidelity results, not live ${mailboxLabel} detection accuracy`} />
      <StatusBanner tone="warning" title="Benchmark-only evidence">
        These fixed fidelity results are benchmark metrics, not live {mailboxLabel} detection accuracy.
      </StatusBanner>
      <VuiBox className="grid-cards">
        <MetricCard title="Accuracy Fidelity" value={`${((benchmark.accuracy_fidelity || 0) * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
        <MetricCard title="F1 Fidelity" value={`${((benchmark.f1_fidelity || 0) * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
        <MetricCard title="Error Fidelity" value={`${((benchmark.error_fidelity || 0) * 100).toFixed(1)}%`} icon={<Activity size={18} />} color="var(--warning)" />
      </VuiBox>
    </VuiBox>
  );
};

export default ModelMonitoring;
