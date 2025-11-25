import { Outlet, useLocation, Link } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { useSidebar } from '../contexts/SidebarContext';
import Sidebar from './Sidebar';
import AIAssistant from './AIAssistant';
import FeedbackButton from './FeedbackButton';
import Footer from './Footer';
import { Sun, Moon, Type, Fish, ChevronRight } from 'lucide-react';

const Layout = () => {
  const location = useLocation();
  const { theme, toggleTheme, textSize, setTextSize } = useTheme();
  const { user } = useAuth();
  const { effectiveCollapsed } = useSidebar();

  const cycleTextSize = () => {
    const sizes = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(textSize);
    const nextIndex = (currentIndex + 1) % sizes.length;
    setTextSize(sizes[nextIndex]);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 overflow-x-hidden">
      {/* Skip Navigation Links for 508 Compliance */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#footer" className="skip-link">
        Skip to footer
      </a>

      {/* Sidebar Navigation */}
      <Sidebar user={user} />

      {/* Top Header Bar */}
      <header
        className={`fixed top-0 right-0 h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-30 transition-all duration-300 ${
          effectiveCollapsed ? 'left-14' : 'left-48'
        }`}
      >
        <div className="h-full px-4 flex items-center justify-between overflow-hidden">
          {/* Breadcrumb Navigation */}
          <div className="flex items-center gap-2 min-w-0 flex-1">
            {/* Logo/Home Link */}
            <Link
              to="/"
              className="flex items-center gap-2 flex-shrink-0 hover:opacity-80 transition-opacity"
              title="SAFMC FMP Tracker Home"
            >
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center">
                <Fish className="w-4 h-4 text-white" />
              </div>
              <span className="text-sm font-semibold text-gray-900 dark:text-white hidden sm:block">
                SAFMC FMP
              </span>
            </Link>

            {/* Separator & Page Title */}
            {location.pathname !== '/' && (
              <>
                <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <h1 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {getPageTitle(location.pathname)}
                </h1>
              </>
            )}
          </div>

          {/* Theme Controls */}
          <div className="flex items-center gap-1 flex-shrink-0">
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
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main
        id="main-content"
        role="main"
        aria-label="Main content"
        className={`pt-14 min-h-screen transition-all duration-300 overflow-x-hidden ${
          effectiveCollapsed ? 'pl-14' : 'pl-48'
        }`}
      >
        <div className="p-6 max-w-full">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <Footer />

      {/* AI Assistant - Available on all pages */}
      <AIAssistant />

      {/* Feedback Button */}
      <FeedbackButton component={getPageTitle(location.pathname)} />
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
