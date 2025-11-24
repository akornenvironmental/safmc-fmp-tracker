import { Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSidebar } from '../contexts/SidebarContext';
import Sidebar from './Sidebar';
import AIAssistant from './AIAssistant';

const Layout = () => {
  const location = useLocation();
  const { user } = useAuth();
  const { effectiveCollapsed } = useSidebar();

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Skip Navigation Links for 508 Compliance */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#footer" className="skip-link">
        Skip to footer
      </a>

      {/* Sidebar Navigation */}
      <Sidebar user={user} />

      {/* Top Header Bar - page title only */}
      <header
        className={`fixed top-0 right-0 h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-30 transition-all duration-300 ${
          effectiveCollapsed ? 'left-14' : 'left-48'
        }`}
      >
        <div className="h-full px-4 flex items-center">
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
            {getPageTitle(location.pathname)}
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main
        id="main-content"
        role="main"
        aria-label="Main content"
        className={`pt-14 min-h-screen transition-all duration-300 ${
          effectiveCollapsed ? 'pl-14' : 'pl-48'
        }`}
      >
        <div className="p-6">
          <Outlet />
        </div>

        {/* Footer */}
        <footer id="footer" className="bg-brand-blue text-white mt-auto">
          <div className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold">SAFMC FMP Tracker</p>
                <p className="text-xs text-blue-200 mt-1">
                  Fishery Management Plan Tracking System
                </p>
              </div>
              <div className="text-xs text-blue-200">
                <p>v1.0.0 | Built by <a href="https://akornenvironmental.com" className="underline hover:text-white">akorn environmental</a></p>
                <p className="mt-1">Data from SAFMC.net, SEDAR, and NOAA</p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-blue-400/30 text-xs text-blue-200">
              <p>This system uses AI-powered tools. All AI-generated information should be reviewed for accuracy.</p>
            </div>
          </div>
        </footer>
      </main>

      {/* AI Assistant - Available on all pages */}
      <AIAssistant />
    </div>
  );
};

// Helper function to get page title from path
function getPageTitle(pathname) {
  const titles = {
    '/': 'Dashboard',
    '/actions': 'Amendment Actions',
    '/meetings': 'Council Meetings',
    '/comments': 'Public Comments',
    '/stocks': 'Stock Assessments',
    '/compare': 'Compare Actions',
    '/workplan': 'Workplan',
    '/admin/logs': 'Activity Logs',
    '/admin/users': 'User Management',
    '/privacy': 'Privacy Policy',
    '/terms': 'Terms of Service',
  };

  // Check for exact match first
  if (titles[pathname]) return titles[pathname];

  // Check for partial matches (for dynamic routes)
  for (const [path, title] of Object.entries(titles)) {
    if (pathname.startsWith(path) && path !== '/') return title;
  }

  return 'SAFMC FMP Tracker';
}

export default Layout;
