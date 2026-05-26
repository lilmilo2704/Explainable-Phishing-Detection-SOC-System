import { NavLink } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  List, 
  Archive, 
  Search, 
  FileText, 
  Activity, 
  MessageSquare,
  Settings,
  RefreshCcw
} from 'lucide-react';
import { fetchMailboxProviders, syncMailbox } from '../api';
import { GradientBorder, VuiBox, VuiButton, VuiTypography } from './vision';

const providerLabel = (provider) => {
  if (provider === 'mock') return 'Mock fixture';
  if (provider === 'gmail') return 'Gmail';
  return provider ? provider.replaceAll('_', ' ') : 'Mailbox';
};

const Sidebar = ({ mobileOpen = false, onClose }) => {
  const [syncing, setSyncing] = useState(false);
  const [syncNote, setSyncNote] = useState('');
  const [provider, setProvider] = useState('');

  useEffect(() => {
    let active = true;
    fetchMailboxProviders()
      .then((data) => {
        if (active) setProvider(data.default_provider || '');
      })
      .catch(() => {
        if (active) setProvider('');
      });
    return () => {
      active = false;
    };
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    setSyncNote('');
    try {
      const payload = { limit: 25, actor: 'analyst' };
      if (provider) payload.provider = provider;
      const result = await syncMailbox(payload);
      setProvider(result.provider || provider);
      setSyncNote(`${providerLabel(result.provider)}: scanned ${result.scanned}; skipped ${result.skipped}; failed ${result.failed}`);
      window.dispatchEvent(new CustomEvent('phishguard:mailbox-synced', { detail: result }));
    } catch {
      setSyncNote('Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <aside className={`sidebar ${mobileOpen ? 'is-open' : ''}`}>
      <VuiBox className="sidebar-header">
        <ShieldAlert size={28} color="var(--accent-blue)" />
        <VuiTypography variant="button" textGradient fontWeight="bold" className="brand-label">
          PhishGuard SOC
        </VuiTypography>
      </VuiBox>
      <VuiBox className="sidebar-section-label">
        <VuiTypography variant="caption" color="text" fontWeight="bold">Analyst Workspace</VuiTypography>
      </VuiBox>
      <VuiBox component="nav" className="sidebar-nav">
        <NavLink to="/" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <LayoutDashboard size={20} />
          Overview
        </NavLink>
        <NavLink to="/queue" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <List size={20} />
          Detection Queue
        </NavLink>
        <NavLink to="/quarantine" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Archive size={20} />
          Quarantine
        </NavLink>
        <NavLink to="/investigation" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Search size={20} />
          Email Investigation
        </NavLink>
        <NavLink to="/global-explanation" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <FileText size={20} />
          Global Explanation
        </NavLink>
        <NavLink to="/feedback-review" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <MessageSquare size={20} />
          Feedback Review
        </NavLink>
        <NavLink to="/model-monitoring" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Activity size={20} />
          Model Monitoring
        </NavLink>
        <NavLink to="/settings" onClick={onClose} className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Settings size={20} />
          Settings
        </NavLink>
      </VuiBox>
      <VuiBox className="sidebar-footer">
        <GradientBorder>
          <VuiBox className="sidebar-operation-card">
            <VuiTypography variant="caption" color="text">{provider ? `${providerLabel(provider)} mailbox` : 'Configured mailbox'}</VuiTypography>
            <VuiTypography variant="button" fontWeight="bold">Manual Sync Only</VuiTypography>
            <VuiButton color="info" variant="gradient" className="sync-button" onClick={handleSync} disabled={syncing}>
              <RefreshCcw size={16} />
              {syncing ? 'Syncing...' : `Sync ${providerLabel(provider)}`}
            </VuiButton>
            {syncNote ? <VuiTypography variant="caption" color="text" className="sync-note">{syncNote}</VuiTypography> : null}
          </VuiBox>
        </GradientBorder>
      </VuiBox>
    </aside>
  );
};

export default Sidebar;
