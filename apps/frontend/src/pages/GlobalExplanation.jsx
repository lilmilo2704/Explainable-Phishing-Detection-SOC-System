import { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { fetchGlobalExplanation } from '../api';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ErrorState, LoadingState, PageHeader, Panel, SectionHeader } from '../components/ui';
import { VuiBox } from '../components/vision';

const GlobalExplanation = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try { setData(await fetchGlobalExplanation()); }
      catch { setError('Unable to load global explanation data. Retry.'); }
      finally { setLoading(false); }
    };
    loadData();
  }, []);

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading global explanation..." /></VuiBox>;
  if (error || !data || data.model_failed) return <VuiBox className="page-content"><ErrorState message={error || 'Unable to load global explanation data. Retry.'} /></VuiBox>;

  const features = (data.top_features || []).slice(0, 10);

  return (
    <VuiBox className="page-content">
      <PageHeader title="Global Explanation" description="Model-level behaviour and surrogate reliability; these indicators are not proof for a single message." />

      <Panel style={{ marginBottom: 16 }}>
        <SectionHeader title="Model Behaviour Summary" subtitle="Teacher and surrogate pair for this explanation run" />
        <div className="model-pair-line">
          <span>Teacher Model: <strong>{data.model_name} {data.model_version}</strong></span>
          <span>Surrogate Model: <strong>{data.surrogate_name} {data.surrogate_version}</strong></span>
        </div>
      </Panel>

      <VuiBox className="grid-cards">
        <MetricCard title="Accuracy Fidelity" value={`${(data.accuracy_fidelity * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
        <MetricCard title="F1 Fidelity" value={`${(data.f1_fidelity * 100).toFixed(1)}%`} icon={<Activity size={18} />} />
        <MetricCard title="Error Fidelity" value={`${(data.error_fidelity * 100).toFixed(1)}%`} icon={<Activity size={18} />} color="var(--warning)" />
      </VuiBox>

      <VuiBox className="grid-2">
        <Panel>
          <SectionHeader title="Global Feature Importance" subtitle="Top factors used by the detector model" />
          <div style={{ height: 260, marginBottom: 14 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={features}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="feature" tick={{ fill: 'var(--chart-axis)', fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={58} />
                <YAxis tick={{ fill: 'var(--chart-axis)', fontSize: 11 }} />
                <Tooltip formatter={(v) => Number(v).toFixed(4)} />
                <Area type="monotone" dataKey="importance" stroke="var(--chart-primary)" fill="var(--chart-primary-fill)" fillOpacity={0.42} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'grid', gap: 8, fontSize: 13 }}>
            {features.map((f) => <div key={f.feature}>{f.feature}: <strong>{(f.importance || 0).toFixed(3)}</strong></div>)}
          </div>
        </Panel>

        <Panel>
          <SectionHeader title="Failure Pattern Summary" subtitle="Patterns observed in model mistakes" />
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>False Positive Pattern</div>
            <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-2)', fontSize: 13 }}>
              {(data.failure_patterns?.false_positives || []).map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>False Negative Pattern</div>
            <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-2)', fontSize: 13 }}>
              {(data.failure_patterns?.false_negatives || []).map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          </div>
        </Panel>
      </VuiBox>
    </VuiBox>
  );
};

export default GlobalExplanation;
