import { VuiBadge, VuiBox, VuiButton, VuiTypography } from '../vision';

export const PageHeader = ({ title, description, right }) => (
  <VuiBox className="page-header">
    <VuiBox>
      <VuiTypography variant="h2" fontWeight="bold" className="page-title">{title}</VuiTypography>
      {description ? <VuiTypography variant="body" color="text" className="page-description">{description}</VuiTypography> : null}
    </VuiBox>
    {right || null}
  </VuiBox>
);

export const Panel = ({ children, className = '', style }) => (
  <VuiBox component="section" className={`panel ${className}`.trim()} style={style}>{children}</VuiBox>
);

export const SectionHeader = ({ title, subtitle }) => (
  <VuiBox className="section-header">
    <VuiTypography variant="h3" fontWeight="bold" className="section-title">{title}</VuiTypography>
    {subtitle ? <VuiTypography variant="caption" color="text" className="section-subtitle">{subtitle}</VuiTypography> : null}
  </VuiBox>
);

export const EmptyState = ({ message = 'No data available.' }) => <VuiBox className="state"><VuiTypography color="text">{message}</VuiTypography></VuiBox>;
export const LoadingState = ({ message = 'Loading...' }) => <VuiBox className="state"><VuiTypography color="text">{message}</VuiTypography></VuiBox>;
export const ErrorState = ({ message = 'Unable to load data.' }) => <VuiBox className="state"><VuiTypography color="text">{message}</VuiTypography></VuiBox>;

export const ActionButton = ({ children, variant = 'primary', ...props }) => (
  <VuiButton color={variant === 'primary' ? 'info' : variant === 'danger' ? 'error' : variant} variant="gradient" className={`btn ${variant}`} {...props}>{children}</VuiButton>
);

const riskToClass = {
  low: 'badge-low', medium: 'badge-medium', high: 'badge-high', critical: 'badge-critical'
};

const displayLabel = (value) => {
  const labels = {
    pending_review: 'Awaiting Review',
    in_review: 'In Review',
    quarantined: 'Quarantined',
    phishing: 'Phishing',
    legitimate: 'Legitimate',
    released: 'Released',
    confirmed_malicious: 'Confirmed Phishing',
    false_positive: 'False Positive',
    false_negative: 'False Negative',
    invalid_pair: 'Invalid Pair',
    matched: 'Matched',
    new: 'Awaiting Review',
    none: 'No Action',
  };
  const key = (value || '').toLowerCase();
  return labels[key] || key.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) || 'Unknown';
};

export const RiskBadge = ({ risk }) => <VuiBadge className={`badge ${riskToClass[(risk || '').toLowerCase()] || 'badge-neutral'}`} color={(risk || '').toLowerCase() === 'critical' || (risk || '').toLowerCase() === 'high' ? 'error' : (risk || '').toLowerCase() === 'medium' ? 'warning' : 'info'}>{displayLabel(risk)}</VuiBadge>;
export const StatusBadge = ({ status }) => {
  const val = (status || '').toLowerCase();
  const cls = val.includes('quarantine') || val.includes('phishing') ? 'badge-high' : val.includes('released') || val.includes('legitimate') || val.includes('closed') ? 'badge-safe' : val.includes('pending') || val.includes('review') ? 'badge-pending' : 'badge-neutral';
  const color = cls === 'badge-high' ? 'error' : cls === 'badge-safe' ? 'success' : cls === 'badge-pending' ? 'warning' : 'info';
  return <VuiBadge className={`badge ${cls}`} color={color}>{displayLabel(status)}</VuiBadge>;
};
export const ConfidenceBadge = ({ confidence }) => {
  const pct = confidence != null ? `${(confidence * 100).toFixed(0)}%` : 'N/A';
  return <VuiBadge className="badge badge-neutral" color="info">{pct}</VuiBadge>;
};

export const DataTable = ({ columns, rows, keyField = 'id', onRowClick, selectedKey, emptyText = 'No records found.' }) => (
  <VuiBox className="data-table-wrap">
    <table className="data-table">
      <thead><tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr></thead>
      <tbody>
        {rows.length === 0 ? <tr><td colSpan={columns.length}><EmptyState message={emptyText} /></td></tr> : rows.map((row) => (
          <tr
            key={row[keyField]}
            className={`${onRowClick ? 'data-row-action' : ''} ${selectedKey === row[keyField] ? 'data-row-selected' : ''}`.trim()}
            onClick={onRowClick ? () => onRowClick(row) : undefined}
            onKeyDown={onRowClick ? (event) => {
              if (event.target === event.currentTarget && (event.key === 'Enter' || event.key === ' ')) {
                event.preventDefault();
                onRowClick(row);
              }
            } : undefined}
            tabIndex={onRowClick ? 0 : undefined}
          >
            {columns.map((c) => <td key={c.key}>{c.render ? c.render(row) : row[c.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </VuiBox>
);

export const FilterBar = ({ children }) => <VuiBox className="filter-bar">{children}</VuiBox>;
