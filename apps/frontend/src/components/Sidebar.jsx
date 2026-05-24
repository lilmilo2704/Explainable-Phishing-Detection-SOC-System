import { NavLink } from 'react-router-dom';
import { useState } from 'react';
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
import { syncMailbox } from '../api';
import { GradientBorder, VuiBox, VuiButton, VuiTypography } from './vision';

const Sidebar = ({ mobileOpen = false, onClose }) => {
  const [syncing, setSyncing] = useState(false);
  const [syncNote, setSyncNote] = useState('');

  const handleSync = async () => {
    setSyncing(true);
    setSyncNote('');
    try {
      const result = await syncMailbox({ provider: 'gmail', limit: 25, actor: 'analyst' });
      setSyncNote(`Scanned ${result.scanned}; skipped ${result.skipped}; failed ${result.failed}`);
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
            <VuiTypography variant="caption" color="text">Gmail prototype</VuiTypography>
            <VuiTypography variant="button" fontWeight="bold">Manual Sync Only</VuiTypography>
            <VuiButton color="info" variant="gradient" className="sync-button" onClick={handleSync} disabled={syncing}>
              <RefreshCcw size={16} />
              {syncing ? 'Syncing...' : 'Sync Gmail'}
            </VuiButton>
            {syncNote ? <VuiTypography variant="caption" color="text" className="sync-note">{syncNote}</VuiTypography> : null}
          </VuiBox>
        </GradientBorder>
      </VuiBox>
    </aside>
  );
};

export default Sidebar;
