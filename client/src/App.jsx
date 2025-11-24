import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { SidebarProvider } from './contexts/SidebarContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import AIAssistant from './components/AIAssistant';
import Dashboard from './pages/DashboardEnhanced';
import ActionsEnhanced from './pages/ActionsEnhanced';
import ActionsNew from './pages/ActionsNew';
import MeetingsEnhanced from './pages/MeetingsEnhanced';
import MeetingCalendar from './pages/MeetingCalendar';
import CommentsEnhanced from './pages/CommentsEnhanced';
import SpeciesStocks from './pages/SpeciesStocks';
import Workplan from './pages/Workplan';
import SpeciesProfile from './pages/SpeciesProfile';
import Compare from './pages/Compare';
import UserManagement from './pages/UserManagement';
import ActivityLogs from './pages/ActivityLogs';
import Login from './pages/Login';
import VerifyLogin from './pages/VerifyLogin';

// Build version to force new asset hash - DO NOT REMOVE
const BUILD_VERSION = '2025-11-23-v4-comments-ui-fix';

function App() {
  // Log build version on mount (forces this code into bundle)
  if (typeof window !== 'undefined' && !window.__BUILD_LOGGED__) {
    console.log('Build:', BUILD_VERSION);
    window.__BUILD_LOGGED__ = true;
  }

  return (
    <ThemeProvider>
      <AuthProvider>
        <SidebarProvider>
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
              <Route path="actions-new" element={<ActionsNew />} />
              <Route path="meetings" element={<MeetingsEnhanced />} />
              <Route path="calendar" element={<MeetingCalendar />} />
              <Route path="comments" element={<CommentsEnhanced />} />
              <Route path="stocks" element={<SpeciesStocks />} />
              <Route path="species" element={<SpeciesStocks />} /> {/* Redirect old route */}
              <Route path="assessments" element={<SpeciesStocks />} /> {/* Redirect old route */}
              <Route path="workplan" element={<Workplan />} />
              <Route path="species/:speciesName" element={<SpeciesProfile />} />
              <Route path="compare" element={<Compare />} />
              <Route path="admin/users" element={<UserManagement />} />
              <Route path="admin/logs" element={<ActivityLogs />} />
            </Route>
          </Routes>
            <AIAssistant />
            <ToastContainer position="top-right" autoClose={3000} />
          </Router>
        </SidebarProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
