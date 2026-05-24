import { useEffect, useState } from 'react';
import { Target, Activity, ShieldCheck, CheckCircle } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { fetchModelHealth } from '../api';
import { ErrorState, LoadingState, PageHeader, Panel, SectionHeader } from '../components/ui';
import { VuiBox } from '../components/vision';

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
  }, []);

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading model monitoring..." /></VuiBox>;
  if (error || !health) return <VuiBox className="page-content"><ErrorState message={error || 'Unable to load model monitoring data. Retry.'} /></VuiBox>;

  return (
    <VuiBox className="page-content">
      <PageHeader title="Model Monitoring" description="Deployed detector performance, explanation reliability, and analyst-confirmed feedback status." />

      <Panel style={{ marginBottom: 16 }}>
        <SectionHeader title="Current Model Pair" subtitle="Detector and surrogate used for decisions and explanations" />
        <div className="summary-grid">
          <div>Current Detector Model: <strong>{health.model_name || 'Random Forest'} {health.model_version || 'v1'}</strong></div>
          <div>Current Surrogate Model: <strong>{health.surrogate_name || 'EBM'} {health.surrogate_version || 'v1'}</strong></div>
        </div>
      </Panel>

      <SectionHeader title="Detection Performance" />
      <VuiBox className="grid-cards">
        <MetricCard title="Accuracy" value={`${(health.accuracy * 100).toFixed(1)}%`} icon={<Target size={18} />} />
        <MetricCard title="Precision" value={`${(health.precision * 100).toFixed(1)}%`} icon={<ShieldCheck size={18} />} />
        <MetricCard title="Recall" value={`${(health.recall * 100).toFixed(1)}%`} icon={<CheckCircle size={18} />} />
        <MetricCard title="F1 Score" value={`${(health.f1_score * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
      </VuiBox>

      <SectionHeader title="Explanation Fidelity" />
      <VuiBox className="grid-cards">
        <MetricCard title="Accuracy Fidelity" value={`${(health.accuracy_fidelity * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
        <MetricCard title="F1 Fidelity" value={`${(health.f1_fidelity * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
        <MetricCard title="Error Fidelity" value={`${(health.error_fidelity * 100).toFixed(1)}%`} icon={<Activity size={18} />} color="var(--warning)" />
      </VuiBox>

      <SectionHeader title="Feedback Governance" />
      <VuiBox className="grid-cards">
        <MetricCard title="Confirmed False Positives" value={health.false_positives ?? 0} icon={<ShieldCheck size={18} />} color="var(--warning)" />
        <MetricCard title="Confirmed False Negatives" value={health.false_negatives ?? 0} icon={<ShieldCheck size={18} />} color="var(--danger)" />
        <MetricCard title="Pending Feedback" value={health.pending_feedback ?? 0} icon={<Activity size={18} />} />
        <MetricCard title="Export Candidates" value={health.improvement_dataset_candidates ?? 0} icon={<CheckCircle size={18} />} color="var(--success)" />
      </VuiBox>
    </VuiBox>
  );
};

export default ModelMonitoring;
