import { Panel, SectionHeader, StatusBadge, StatusBanner } from './ui';

const providerLabel = (provider) => {
  if (provider === 'mock') return 'mock fixture mailbox';
  if (provider === 'gmail') return 'Gmail mailbox';
  return provider ? `${provider.replaceAll('_', ' ')} mailbox` : 'configured mailbox';
};

const SyncStatusPanel = ({ syncStatus }) => {
  if (!syncStatus) return null;
  const failed = (syncStatus.failed || 0) > 0 || syncStatus.status === 'failed';
  const mailboxLabel = providerLabel(syncStatus.provider);
  return (
    <Panel>
      <SectionHeader title="Last Sync Status" subtitle={`Manual ${mailboxLabel} sync operational state`} />
      {failed ? (
        <StatusBanner tone="error" title="Mailbox sync needs attention">
          One or more messages failed during sync and remain marked for review.
        </StatusBanner>
      ) : null}
      <div className="summary-grid">
        <div>Provider: <strong>{mailboxLabel}</strong></div>
        <div>Status: <StatusBadge status={syncStatus.status || 'not_run'} /></div>
        <div>Scanned: <strong>{syncStatus.scanned || 0}</strong></div>
        <div>Skipped: <strong>{syncStatus.skipped || 0}</strong></div>
        <div>Failed: <strong>{syncStatus.failed || 0}</strong></div>
        <div>Last run: <strong>{syncStatus.last_sync_time ? new Date(syncStatus.last_sync_time).toLocaleString() : 'Not run'}</strong></div>
      </div>
      {(syncStatus.failures || []).length ? (
        <div className="governance-note">{syncStatus.failures.map((row) => row.subject || row.email_id).join(', ')}</div>
      ) : null}
    </Panel>
  );
};

export default SyncStatusPanel;
