import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import AIAssistant from './components/AIAssistant';
import Dashboard from './pages/Dashboard';
import ActionsEnhanced from './pages/ActionsEnhanced';
import MeetingsEnhanced from './pages/MeetingsEnhanced';
import CommentsEnhanced from './pages/CommentsEnhanced';
import StockAssessments from './pages/StockAssessments';
import Login from './pages/Login';
import VerifyLogin from './pages/VerifyLogin';

// Build version to force new asset hash - DO NOT REMOVE
const BUILD_VERSION = '2025-11-10-v4-header-light-mode-fix';

function App() {
  // Log build version on mount (forces this code into bundle)
  if (typeof window !== 'undefined' && !window.__BUILD_LOGGED__) {
    console.log('Build:', BUILD_VERSION);
    window.__BUILD_LOGGED__ = true;
  }

  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/auth/verify" element={<VerifyLogin />} />

            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="actions" element={<ActionsEnhanced />} />
              <Route path="meetings" element={<MeetingsEnhanced />} />
              <Route path="comments" element={<CommentsEnhanced />} />
              <Route path="assessments" element={<StockAssessments />} />
            </Route>
          </Routes>
          <AIAssistant />
          <ToastContainer position="top-right" autoClose={3000} />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
