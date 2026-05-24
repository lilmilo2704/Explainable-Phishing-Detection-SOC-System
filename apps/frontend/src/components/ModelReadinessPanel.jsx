import { Panel, SectionHeader, StatusBadge, StatusBanner } from './ui';

const ModelReadinessPanel = ({ readiness }) => {
  if (!readiness) return null;
  const safe = readiness.safe_for_live_prediction;
  return (
    <Panel>
      <SectionHeader title="Model Readiness Check" subtitle="Validation required before trusted Gmail actions" />
      {!safe ? (
        <StatusBanner tone="warning" title="Shadow mode: trusted prediction blocked">
          {readiness.recommended_action_if_unsafe}
        </StatusBanner>
      ) : (
        <StatusBanner tone="success" title="Pipeline validated">
          Trusted high-risk decisions can apply the quarantine policy.
        </StatusBanner>
      )}
      <div className="summary-grid readiness-grid">
        <div>Teacher model: <StatusBadge status={readiness.teacher_model_loaded ? 'ready' : 'missing'} /></div>
        <div>Surrogate model: <StatusBadge status={readiness.surrogate_model_loaded ? 'ready' : 'missing'} /></div>
        <div>Training preprocessor: <StatusBadge status={readiness.preprocessor_loaded ? 'ready' : 'missing'} /></div>
        <div>Feature order: <StatusBadge status={readiness.feature_order_match ? 'recovered' : 'missing'} /></div>
      </div>
      {readiness.feature_order_match && !readiness.preprocessor_loaded ? (
        <p className="subtle-text">
          Exact processed column order recovered from the fitted surrogate; the original fitted preprocessor is still required.
        </p>
      ) : null}
      {(readiness.warnings || []).length ? (
        <ul className="warning-list">
          {readiness.warnings.map((warning) => <li key={warning}>{warning}</li>)}
        </ul>
      ) : null}
    </Panel>
  );
};

export default ModelReadinessPanel;
