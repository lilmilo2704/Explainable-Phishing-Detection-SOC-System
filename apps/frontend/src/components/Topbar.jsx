import { useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Menu } from 'lucide-react';
import { DashboardNavbar, VuiBadge, VuiButton } from './vision';

const Topbar = ({ onOpenNavigation }) => {
  const location = useLocation();
  const [theme, setTheme] = useState(() => (
    localStorage.getItem('theme_mode') === 'light' ? 'light' : 'dark'
  ));

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme_mode', next);
  };

  const getPageTitle = () => {
    if (location.pathname.startsWith('/investigation/')) return 'Email Investigation';
    switch(location.pathname) {
      case '/': return 'Overview';
      case '/queue': return 'Detection Queue';
      case '/quarantine': return 'Quarantine';
      case '/investigation': return 'Email Investigation';
      case '/global-explanation': return 'Global Explanation';
      case '/feedback-review': return 'Feedback Review';
      case '/model-monitoring': return 'Model Monitoring';
      case '/settings': return 'Settings';
      default: return 'PhishGuard';
    }
  };

  return (
    <DashboardNavbar
      title={getPageTitle()}
      context="Security Operations / Mailbox Protection"
      leading={(
        <VuiButton iconOnly variant="outlined" color="info" className="menu-toggle" aria-label="Open navigation" onClick={onOpenNavigation}>
          <Menu size={20} />
        </VuiButton>
      )}
      actions={(
        <>
        <VuiButton variant="outlined" color="info" className="theme-toggle" onClick={toggleTheme} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </VuiButton>
        <VuiBadge color="info" variant="contained" className="analyst-badge">SOC Analyst Console</VuiBadge>
        </>
      )}
    />
  );
};

export default Topbar;
