import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { useSidebar } from '../contexts/SidebarContext';
import Sidebar from './Sidebar';
import AIAssistant from './AIAssistant';
import { Sun, Moon, Type } from 'lucide-react';

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme, textSize, setTextSize } = useTheme();
  const { user, logout } = useAuth();
  const { effectiveCollapsed } = useSidebar();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const cycleTextSize = () => {
    const sizes = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(textSize);
    const nextIndex = (currentIndex + 1) % sizes.length;
    setTextSize(sizes[nextIndex]);
  };

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
      <Sidebar user={user} onLogout={handleLogout} />

      {/* Top Header Bar - for controls only */}
      <header
        className={`fixed top-0 right-0 h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-30 transition-all duration-300 ${
          effectiveCollapsed ? 'left-16' : 'left-64'
        }`}
      >
        <div className="h-full px-4 flex items-center justify-between">
          {/* Page Title */}
          <div className="flex items-center">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              {getPageTitle(location.pathname)}
            </h1>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            {/* Text Size Toggle */}
            <button
              onClick={cycleTextSize}
              className="flex items-center justify-center w-9 h-9 text-gray-500 hover:text-brand-blue hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title={`Text size: ${textSize} (click to cycle)`}
              aria-label={`Text size: ${textSize}. Click to cycle through sizes.`}
            >
              <Type className="w-4 h-4" />
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              className="flex items-center justify-center w-9 h-9 text-gray-500 hover:text-brand-blue hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
              aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>

            {/* User Info */}
            {user && (
              <div className="flex items-center ml-2 pl-2 border-l border-gray-200 dark:border-gray-700">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center text-white text-sm font-medium">
                  {(user.name || user.email || '?').charAt(0).toUpperCase()}
                </div>
                <div className="ml-2 hidden sm:block">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.name || user.email}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main
        id="main-content"
        role="main"
        aria-label="Main content"
        className={`pt-14 min-h-screen transition-all duration-300 ${
          effectiveCollapsed ? 'pl-16' : 'pl-64'
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
