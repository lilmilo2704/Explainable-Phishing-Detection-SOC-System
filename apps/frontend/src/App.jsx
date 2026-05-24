import { lazy, Suspense, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import { DashboardLayout, Footer } from './components/vision';
import { LoadingState } from './components/ui';

const Overview = lazy(() => import('./pages/Overview'));
const DetectionQueue = lazy(() => import('./pages/DetectionQueue'));
const Quarantine = lazy(() => import('./pages/Quarantine'));
const EmailInvestigation = lazy(() => import('./pages/EmailInvestigation'));
const GlobalExplanation = lazy(() => import('./pages/GlobalExplanation'));
const FeedbackReview = lazy(() => import('./pages/FeedbackReview'));
const ModelMonitoring = lazy(() => import('./pages/ModelMonitoring'));
const Settings = lazy(() => import('./pages/Settings'));

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
          <Suspense fallback={<LoadingState message="Loading workspace..." />}>
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
          </Suspense>
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
