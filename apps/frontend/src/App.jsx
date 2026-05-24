import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import { DashboardLayout, Footer } from './components/vision';
import Overview from './pages/Overview';
import DetectionQueue from './pages/DetectionQueue';
import Quarantine from './pages/Quarantine';
import EmailInvestigation from './pages/EmailInvestigation';
import GlobalExplanation from './pages/GlobalExplanation';
import FeedbackReview from './pages/FeedbackReview';
import ModelMonitoring from './pages/ModelMonitoring';
import Settings from './pages/Settings';

function DashboardShell() {
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <DashboardLayout>
      <div className="app-container">
      <Sidebar mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
      {mobileNavOpen ? (
        <button
          type="button"
          className="nav-overlay"
          aria-label="Close navigation"
          onClick={() => setMobileNavOpen(false)}
        />
      ) : null}
      <div className="main-content">
        <Topbar onOpenNavigation={() => setMobileNavOpen(true)} />
        <div className="route-stage">
          <div className="page-route" key={location.pathname}>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/queue" element={<DetectionQueue />} />
            <Route path="/quarantine" element={<Quarantine />} />
            <Route path="/investigation" element={<EmailInvestigation />} />
            <Route path="/investigation/:id" element={<EmailInvestigation />} />
            <Route path="/global-explanation" element={<GlobalExplanation />} />
            <Route path="/feedback-review" element={<FeedbackReview />} />
            <Route path="/model-monitoring" element={<ModelMonitoring />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
          </div>
        </div>
        <Footer />
      </div>
    </div>
    </DashboardLayout>
  );
}

function App() {
  return (
    <Router>
      <DashboardShell />
    </Router>
  );
}

export default App;
