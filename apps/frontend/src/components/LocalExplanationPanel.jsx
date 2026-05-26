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

const formatTimestamp = (value) => {
  if (!value) return 'Unavailable';
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? 'Unavailable' : timestamp.toLocaleString();
};

const LocalExplanationPanel = ({ emailId, onExplanationStateChange }) => {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!emailId) return;
    let active = true;
    onExplanationStateChange?.({ status: 'loading', data: null });
    const loadExpl = async () => {
      try {
        const data = await fetchLocalExplanation(emailId);
        if (!active) return;
        setExplanation(data);
        onExplanationStateChange?.({ status: 'loaded', data });
      } catch {
        if (!active) return;
        setError('Unable to load local explanation for this email.');
        onExplanationStateChange?.({ status: 'unavailable', data: null });
      } finally {
        if (active) setLoading(false);
      }
    };
    loadExpl();
    return () => { active = false; };
  }, [emailId, onExplanationStateChange]);

  if (loading) return <LoadingState message="Loading local explanation..." />;
  if (error) return <ErrorState message={error} />;
  if (!explanation) return <ErrorState message="No local explanation available for this case." />;
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
        {explanation.human_summary || 'A human-readable explanation summary is unavailable for this decision.'}
      </VuiBox>
      {explanation.model_failed || explanation.pipeline_status === 'explanation_unavailable_review_required' ? (
        <StatusBanner tone="warning" title="Explanation unavailable">
          Explanation generation did not complete for this prediction. Review the email evidence manually.
        </StatusBanner>
      ) : null}
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
      
      <VuiBox className="explanation-metadata detail-grid">
        <VuiTypography variant="caption" color="text">Snapshot ID</VuiTypography>
        <VuiTypography variant="caption" color="text">{explanation.snapshot_id || 'Not captured'}</VuiTypography>
        <VuiTypography variant="caption" color="text">Model Version</VuiTypography>
        <VuiTypography variant="caption" color="text">{explanation.model_version || 'Unavailable'}</VuiTypography>
        <VuiTypography variant="caption" color="text">Explainer Method</VuiTypography>
        <VuiTypography variant="caption" color="text">{explanation.explainer_type || 'Unavailable'}</VuiTypography>
        <VuiTypography variant="caption" color="text">Generated</VuiTypography>
        <VuiTypography variant="caption" color="text">{formatTimestamp(explanation.created_at)}</VuiTypography>
      </VuiBox>
      <div className="governance-note">Feature contributions describe model influence and are not proof that an email is malicious.</div>
    </VuiBox>
  );
};

export default LocalExplanationPanel;
