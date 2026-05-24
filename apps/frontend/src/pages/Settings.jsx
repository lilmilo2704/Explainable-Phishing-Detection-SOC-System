import { useEffect, useMemo, useState } from 'react';
import {
  fetchActiveModelConfig,
  fetchModelReadiness,
  fetchModelRegistry,
  saveActiveModelConfig,
} from '../api';
import { ActionButton, ErrorState, LoadingState, PageHeader, Panel, SectionHeader, StatusBadge } from '../components/ui';
import { VuiBox, VuiInput } from '../components/vision';
import ModelReadinessPanel from '../components/ModelReadinessPanel';

const Settings = () => {
  const [registry, setRegistry] = useState({ teachers: [], surrogates: [] });
  const [active, setActive] = useState(null);
  const [teacherId, setTeacherId] = useState('');
  const [surrogateId, setSurrogateId] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [readiness, setReadiness] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [reg, activeCfg, readinessData] = await Promise.all([
          fetchModelRegistry(),
          fetchActiveModelConfig(),
          fetchModelReadiness(),
        ]);
        setRegistry(reg);
        setActive(activeCfg);
        setTeacherId(activeCfg.teacher_model_id);
        setSurrogateId(activeCfg.surrogate_model_id);
        setReadiness(readinessData);
      } catch (e) {
        setError(e.message || 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const teachers = useMemo(() => registry.teachers || [], [registry.teachers]);
  const surrogates = useMemo(() => registry.surrogates || [], [registry.surrogates]);
  const selectedTeacher = useMemo(
    () => teachers.find((t) => t.id === teacherId),
    [teachers, teacherId]
  );
  const compatibleSurrogates = useMemo(() => {
    const valid = new Set(selectedTeacher?.valid_surrogates || []);
    return surrogates.filter((s) => valid.has(s.id));
  }, [surrogates, selectedTeacher]);
  const selectedSurrogate = useMemo(
    () => surrogates.find((s) => s.id === surrogateId),
    [surrogates, surrogateId]
  );
  const isMatched = !!selectedTeacher && (selectedTeacher.valid_surrogates || []).includes(surrogateId);

  const onTeacherChange = (nextTeacherId) => {
    setTeacherId(nextTeacherId);
    const teacher = teachers.find((t) => t.id === nextTeacherId);
    const nextValid = teacher?.valid_surrogates || [];
    const nextAvailable = surrogates.find((s) => nextValid.includes(s.id) && s.available !== false);
    if (!nextValid.includes(surrogateId) || (surrogates.find((s) => s.id === surrogateId)?.available === false)) {
      setSurrogateId(nextAvailable?.id || '');
    }
  };

  const selectedSurrogateUnavailable = selectedSurrogate?.available === false;

  const onSave = async () => {
    setMessage('');
    setError('');
    if (selectedSurrogateUnavailable) {
      setError(selectedSurrogate?.unavailable_reason || 'Selected surrogate is unavailable in this runtime.');
      return;
    }
    try {
      const updated = await saveActiveModelConfig({
        teacher_model_id: teacherId,
        surrogate_model_id: surrogateId,
      });
      setActive(updated);
      setReadiness(await fetchModelReadiness());
      setMessage('Model configuration saved successfully.');
    } catch (e) {
      setError(e.message || 'Failed to save model configuration.');
    }
  };

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading settings..." /></VuiBox>;

  return (
    <VuiBox className="page-content">
      <PageHeader title="Settings" description="Controlled model-pair configuration for detection and global explanation display." />
      {error ? <ErrorState message={error} /> : null}
      <ModelReadinessPanel readiness={readiness} />
      <Panel style={{ marginBottom: '16px' }}>
        <SectionHeader title="Model Configuration" subtitle="Select a compatible detector and global surrogate model pair" />
        <div className="governance-note" style={{ marginBottom: '12px' }}>
          Surrogate explanation models are only valid for the teacher model they were trained to approximate. If the teacher model changes, the surrogate must be changed to a compatible version.
        </div>
        <VuiBox className="form-grid">
          <VuiBox>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-2)' }}>
              Active Teacher Detection Model
            </label>
            <VuiInput component="select" value={teacherId} onChange={(e) => onTeacherChange(e.target.value)} style={{ width: '100%' }}>
              {teachers.map((t) => (
                <option key={t.id} value={t.id}>{t.display_name}</option>
              ))}
            </VuiInput>
            <p style={{ color: 'var(--text-2)', fontSize: '0.8rem' }}>
              {selectedTeacher?.description}
            </p>
          </VuiBox>
          <VuiBox>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-2)' }}>
              Active Surrogate Explanation Model
            </label>
            <VuiInput component="select" value={surrogateId} onChange={(e) => setSurrogateId(e.target.value)} style={{ width: '100%' }}>
              {compatibleSurrogates.map((s) => (
                <option key={s.id} value={s.id} disabled={s.available === false}>
                  {s.display_name}{s.available === false ? ' (Unavailable)' : ''}
                </option>
              ))}
            </VuiInput>
            <p style={{ color: 'var(--text-2)', fontSize: '0.8rem' }}>
              {selectedSurrogate?.description}
            </p>
            {selectedSurrogateUnavailable ? (
              <p style={{ color: 'var(--warning)', fontSize: '0.78rem', marginTop: '4px' }}>
                {selectedSurrogate?.unavailable_reason}
              </p>
            ) : null}
          </VuiBox>
        </VuiBox>
        <ActionButton
          variant="primary"
          onClick={onSave}
          disabled={!surrogateId || selectedSurrogateUnavailable}
          style={{ marginTop: '12px' }}
        >
          Save Model Configuration
        </ActionButton>
        {message ? <div style={{ marginTop: '10px', color: 'var(--success)' }}>{message}</div> : null}
        {error ? <div style={{ marginTop: '10px', color: 'var(--danger)' }}>{error}</div> : null}
      </Panel>

      <Panel>
        <SectionHeader title="Current Active Model" />
        <div className="summary-grid">
          <div>Teacher Model: <strong>{active?.teacher_model_name || '-'}</strong></div>
          <div>Explanation Model: <strong>{active?.surrogate_model_name || '-'}</strong></div>
          <div>Feature Count: <strong>{active?.expected_features || 292}</strong></div>
          <div>
            Status:{' '}
            <StatusBadge status={isMatched ? 'matched' : 'invalid_pair'} />
          </div>
        </div>
      </Panel>
    </VuiBox>
  );
};

export default Settings;
