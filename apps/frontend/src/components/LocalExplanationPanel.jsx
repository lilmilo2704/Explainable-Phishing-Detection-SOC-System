import { useEffect, useState } from 'react';
import { fetchLocalExplanation } from '../api';
import { EmptyState, ErrorState, LoadingState, StatusBanner } from './ui';
import { VuiBox, VuiTypography } from './vision';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const LocalExplanationPanel = ({ emailId }) => {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!emailId) return;
    const loadExpl = async () => {
      try {
        const data = await fetchLocalExplanation(emailId);
        setExplanation(data);
      } catch {
        setError('Unable to load local explanation for this email.');
      } finally {
        setLoading(false);
      }
    };
    loadExpl();
  }, [emailId]);

  if (loading) return <LoadingState message="Loading local explanation..." />;
  if (error) return <ErrorState message={error} />;
  if (!explanation || explanation.model_failed) return <ErrorState message="No local explanation available for this case." />;
  const features = explanation.top_features || [];
  const chartData = [...features]
    .slice(0, 8)
    .map((f) => ({
      feature: f.feature,
      contribution: Number(f.contribution || 0),
      direction: f.direction,
    }))
    .reverse();

  return (
    <VuiBox className="explanation-stack">
      <VuiBox className="explanation-summary">
        {explanation.human_summary}
      </VuiBox>
      {explanation.pipeline_status === 'unsafe_incomplete_features' ? (
        <StatusBanner tone="warning" title="Untrusted explanation context">
          Training preprocessing alignment is incomplete. This does not prove phishing; analyst review is required.
        </StatusBanner>
      ) : null}

      <VuiBox>
        <VuiTypography variant="button" color="text" fontWeight="bold" className="explanation-subtitle">Feature Contribution</VuiTypography>
        {features.length ? <div style={{ height: '260px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis type="number" tick={{ fill: 'var(--text-2)', fontSize: 11 }} />
              <YAxis type="category" dataKey="feature" width={150} tick={{ fill: 'var(--text-2)', fontSize: 11 }} />
              <Tooltip formatter={(value) => Number(value).toFixed(4)} />
              <ReferenceLine x={0} stroke="var(--chart-reference)" />
              <Bar dataKey="contribution" radius={[4, 4, 4, 4]}>
                {chartData.map((entry, idx) => (
                  <Cell
                    key={`${entry.feature}-${idx}`}
                    fill={entry.direction === 'increases_phishing_risk' ? 'var(--danger)' : 'var(--success)'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div> : <EmptyState message="Technical feature contributions are unavailable until the model pipeline is validated." />}
      </VuiBox>

      <VuiBox>
        <VuiTypography variant="button" color="text" fontWeight="bold" className="explanation-subtitle">Top Explanation Factors</VuiTypography>
        {features.length ? <div className="factor-list">
          {features.map((feat, idx) => (
            <div key={idx} className="factor-row">
              <div className="factor-heading">
                <span className="factor-name">{feat.feature}</span>
                <span style={{ color: feat.direction === 'increases_phishing_risk' ? 'var(--danger)' : 'var(--success)' }}>
                  {feat.contribution > 0 ? '+' : ''}{feat.contribution}
                </span>
              </div>
              <div className="factor-reason">
                {feat.human_reason}
              </div>
              <div className="factor-track">
                <div className="factor-fill" style={{ 
                  width: `${Math.min(Math.abs(feat.contribution) * 100 * 2, 100)}%`, 
                  backgroundColor: feat.direction === 'increases_phishing_risk' ? 'var(--danger)' : 'var(--success)' 
                }} />
              </div>
            </div>
          ))}
        </div> : <EmptyState message="No trusted raw contribution details available." />}
      </VuiBox>
      
      <VuiTypography variant="caption" color="text" className="explanation-metadata">
        Explanation generated using: {explanation.explainer_type}
      </VuiTypography>
      <VuiTypography variant="caption" color="text">
        Explainer: {explanation.explainer_type} | Model Version: {explanation.model_version}
      </VuiTypography>
      <div className="governance-note">Feature contributions describe model influence and are not proof that an email is malicious.</div>
    </VuiBox>
  );
};

export default LocalExplanationPanel;
