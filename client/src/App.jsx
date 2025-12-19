import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { SidebarProvider } from './contexts/SidebarContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
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
import Timeline from './pages/Timeline';
import Ecosystem from './pages/Ecosystem';
import UserManagement from './pages/UserManagement';
import ActivityLogs from './pages/ActivityLogs';
import FeedbackManagement from './pages/FeedbackManagement';
import DataManagement from './pages/DataManagement';
import SSCDashboard from './pages/SSC/SSCDashboard';
import SSCMembers from './pages/SSC/SSCMembers';
import SSCMeetings from './pages/SSC/SSCMeetings';
import SSCRecommendations from './pages/SSC/SSCRecommendations';
import CMODDashboard from './pages/CMOD/CMODDashboard';
import CMODWorkshops from './pages/CMOD/CMODWorkshops';
import CMODTopics from './pages/CMOD/CMODTopics';
import ResourceAllocation from './pages/ResourceAllocation';
import UserProfile from './pages/UserProfile';
import Favorites from './pages/Favorites';
import WorkplanUpload from './pages/WorkplanUpload';
import Login from './pages/Login';
import VerifyLogin from './pages/VerifyLogin';
import DevLogin from './pages/DevLogin';

// Build version to force new asset hash - DO NOT REMOVE
const BUILD_VERSION = '2025-11-26-v20-dashboard-status-fix';

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
            <Route path="/dev-login" element={<DevLogin />} />

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
              <Route path="workplan/upload" element={<WorkplanUpload />} />
              <Route path="timeline" element={<Timeline />} />
              <Route path="ecosystem" element={<Ecosystem />} />
              <Route path="species/:speciesName" element={<SpeciesProfile />} />
              <Route path="compare" element={<Compare />} />
              <Route path="resource-allocation" element={<ResourceAllocation />} />
              <Route path="ssc" element={<SSCDashboard />} />
              <Route path="ssc/members" element={<SSCMembers />} />
              <Route path="ssc/meetings" element={<SSCMeetings />} />
              <Route path="ssc/recommendations" element={<SSCRecommendations />} />
              <Route path="cmod" element={<CMODDashboard />} />
              <Route path="cmod/workshops/:id" element={<CMODWorkshops />} />
              <Route path="cmod/topics" element={<CMODTopics />} />
              <Route path="admin/users" element={<UserManagement />} />
              <Route path="admin/logs" element={<ActivityLogs />} />
              <Route path="admin/feedback" element={<FeedbackManagement />} />
              <Route path="admin/data" element={<DataManagement />} />
              <Route path="profile" element={<UserProfile />} />
              <Route path="favorites" element={<Favorites />} />
            </Route>
          </Routes>
            <ToastContainer position="top-right" autoClose={3000} />
          </Router>
        </SidebarProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
