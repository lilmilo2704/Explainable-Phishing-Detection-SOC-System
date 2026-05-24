import { useEffect, useMemo, useState } from 'react';
import { Mail, ShieldAlert, Archive, ClipboardList, AlertTriangle, ShieldX, ShieldCheck, Gauge } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import MetricCard from '../components/MetricCard';
import { fetchEmails, fetchModelReadiness, fetchSummary, fetchSyncStatus } from '../api';
import ModelReadinessPanel from '../components/ModelReadinessPanel';
import SyncStatusPanel from '../components/SyncStatusPanel';
import { DataTable, ErrorState, LoadingState, PageHeader, Panel, RiskBadge, SectionHeader, StatusBadge, StatusBanner } from '../components/ui';
import { VuiBox } from '../components/vision';

const RISK_COLORS = { low: 'var(--chart-axis)', medium: 'var(--warning)', high: 'var(--danger)', critical: 'var(--critical)' };

const Overview = () => {
  const [summary, setSummary] = useState(null);
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [readiness, setReadiness] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [summaryData, emailData, readinessData, syncData] = await Promise.all([
          fetchSummary(), fetchEmails(), fetchModelReadiness(), fetchSyncStatus(),
        ]);
        setSummary(summaryData);
        setEmails(emailData.items || []);
        setReadiness(readinessData);
        setSyncStatus(syncData);
      } catch {
        setError('Unable to load overview data. Retry.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
    window.addEventListener('phishguard:mailbox-synced', loadData);
    return () => window.removeEventListener('phishguard:mailbox-synced', loadData);
  }, []);

  const trendData = useMemo(() => {
    const map = new Map();
    for (const email of emails) {
      const d = new Date(email.received_at);
      if (Number.isNaN(d.getTime())) continue;
      const key = d.toISOString().slice(0, 10);
      if (!map.has(key)) map.set(key, { day: key, total: 0, phishing: 0 });
      const row = map.get(key);
      row.total += 1;
      if (email.prediction === 'phishing') row.phishing += 1;
    }
    return Array.from(map.values()).sort((a, b) => a.day.localeCompare(b.day));
  }, [emails]);

  const riskData = useMemo(() => {
    const counts = { low: 0, medium: 0, high: 0, critical: 0 };
    for (const e of emails) {
      const key = (e.risk_level || 'low').toLowerCase();
      if (counts[key] != null) counts[key] += 1;
    }
    return Object.keys(counts).map((k) => ({ name: k, value: counts[k] }));
  }, [emails]);

  const topDomains = useMemo(() => {
    const map = new Map();
    for (const e of emails) {
      const domain = (e.sender || '').split('@')[1] || 'unknown';
      if (!map.has(domain)) map.set(domain, { id: domain, domain, count: 0, phishing: 0, last_seen: e.received_at });
      const row = map.get(domain);
      row.count += 1;
      if (e.prediction === 'phishing') row.phishing += 1;
      if ((e.received_at || '') > (row.last_seen || '')) row.last_seen = e.received_at;
    }
    return Array.from(map.values()).sort((a, b) => b.phishing - a.phishing).slice(0, 8);
  }, [emails]);

  const highRisk = useMemo(() => emails.filter((e) => ['high', 'critical'].includes((e.risk_level || '').toLowerCase())).slice(0, 12), [emails]);

  if (loading) return <VuiBox className="page-content"><LoadingState message="Loading security overview..." /></VuiBox>;
  if (error || !summary) return <VuiBox className="page-content"><ErrorState message={error || 'Unable to load overview data. Retry.'} /></VuiBox>;

  return (
    <VuiBox className="page-content">
      <PageHeader title="Overview" description="Operational summary of scanned email risk, quarantine activity, and pending analyst review." />
      {!readiness?.safe_for_live_prediction ? (
        <StatusBanner tone="warning" title="Model pipeline incomplete">
          Predictions are recorded as needs-review shadow-mode results until training preprocessing artifacts validate.
        </StatusBanner>
      ) : null}
      <StatusBanner tone="info" title="Live operational metrics">
        Dashboard counts below are calculated from local mailbox records. Research benchmark fidelity is shown separately in Model Monitoring.
      </StatusBanner>

      <VuiBox className="grid-cards">
        <MetricCard title="Emails Scanned" value={summary.emails_scanned} icon={<Mail size={18} />} />
        <MetricCard title="Phishing Detected" value={summary.phishing_detected} icon={<ShieldAlert size={18} />} color="var(--danger)" />
        <MetricCard title="Quarantined Emails" value={summary.quarantined} icon={<Archive size={18} />} color="var(--warning)" />
        <MetricCard title="Pending Review" value={summary.pending_review} icon={<ClipboardList size={18} />} color="var(--warning)" />
        <MetricCard title="Confirmed False Positives" value={summary.false_positive_reports} icon={<ShieldCheck size={18} />} />
        <MetricCard title="Confirmed False Negatives" value={summary.false_negative_reports} icon={<ShieldX size={18} />} color="var(--danger)" />
        <MetricCard title="Average Confidence" value={summary.average_confidence == null ? 'N/A' : `${(summary.average_confidence * 100).toFixed(0)}%`} icon={<Gauge size={18} />} />
        <MetricCard title="High-Risk Cases" value={summary.high_risk_cases} icon={<AlertTriangle size={18} />} color="var(--critical)" />
      </VuiBox>

      <VuiBox className="grid-2" style={{ marginBottom: 16 }}>
        <ModelReadinessPanel readiness={readiness} />
        <SyncStatusPanel syncStatus={syncStatus} />
      </VuiBox>

      <VuiBox className="grid-2" style={{ marginBottom: 16 }}>
        <Panel>
          <SectionHeader title="Detection Trend" subtitle="Phishing and total detections over time" />
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="day" tick={{ fill: 'var(--chart-axis)', fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fill: 'var(--chart-axis)', fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="total" stroke="var(--chart-primary)" fill="var(--chart-primary-fill)" fillOpacity={0.42} />
                <Area type="monotone" dataKey="phishing" stroke="var(--chart-danger)" fill="var(--chart-danger-fill)" fillOpacity={0.42} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel>
          <SectionHeader title="Risk Distribution" subtitle="Current risk mix in scanned emails" />
          <div style={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" outerRadius={80} innerRadius={50}>
                  {riskData.map((r) => <Cell key={r.name} fill={RISK_COLORS[r.name]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </VuiBox>

      <Panel style={{ marginBottom: 16 }}>
        <SectionHeader title="Top Risky Sender Domains" subtitle="Most frequent domains in suspicious detections" />
        <DataTable
          columns={[
            { key: 'domain', label: 'Sender Domain' },
            { key: 'count', label: 'Emails' },
            { key: 'phishing', label: 'Phishing Detected' },
            { key: 'last_seen', label: 'Latest Detection', render: (r) => r.last_seen ? new Date(r.last_seen).toLocaleString() : 'N/A' },
          ]}
          rows={topDomains}
          keyField="domain"
          emptyText="No sender domain data available."
        />
      </Panel>

      <Panel>
        <SectionHeader title="Recent High-Risk Activity" subtitle="High and critical cases requiring analyst attention" />
        <DataTable
          columns={[
            { key: 'id', label: 'Case ID', render: (r) => `CASE-${String(r.id || '').toUpperCase()}` },
            { key: 'received_at', label: 'Received Time', render: (r) => r.received_at ? new Date(r.received_at).toLocaleString() : 'N/A' },
            { key: 'sender', label: 'Sender' },
            { key: 'subject', label: 'Subject' },
            { key: 'risk_level', label: 'Risk', render: (r) => <RiskBadge risk={r.risk_level} /> },
            { key: 'quarantine_status', label: 'Action', render: (r) => <StatusBadge status={r.quarantine_status || 'pending_review'} /> },
          ]}
          rows={highRisk}
          emptyText="No high-risk activity in the selected period."
        />
      </Panel>
    </VuiBox>
  );
};

export default Overview;
