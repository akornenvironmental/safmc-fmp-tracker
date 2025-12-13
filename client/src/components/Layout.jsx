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
        className={`fixed top-0 right-0 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-30 transition-all duration-300 ${
          effectiveCollapsed ? 'left-14' : 'left-52'
        }`}
      >
        <div className="h-full px-4 flex items-center justify-between overflow-hidden">
          {/* Breadcrumb Navigation */}
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {/* Hierarchical Breadcrumb Path */}
            {(() => {
              const breadcrumb = getBreadcrumbPath(location.pathname);

              return (
                <>
                  {/* Path segments and current page */}
                  {breadcrumb.path.map((segment, index) => (
                    <div key={index} className="flex items-center gap-3 flex-shrink-0">
                      {index > 0 && <ChevronRight className="w-5 h-5 text-gray-400" />}
                      <span className="text-lg font-heading text-gray-600 dark:text-gray-400">
                        {segment}
                      </span>
                    </div>
                  ))}
                  {breadcrumb.path.length > 0 && <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />}
                  <h1 className="text-lg font-heading font-semibold text-gray-900 dark:text-white truncate">
                    {breadcrumb.label}
                  </h1>
                </>
              );
            })()}
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
        className={`pt-16 min-h-screen transition-all duration-300 overflow-x-hidden ${
          effectiveCollapsed ? 'pl-14' : 'pl-52'
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
      <FeedbackButton component={getBreadcrumbPath(location.pathname).label} />
    </div>
  );
};

// Helper function to generate hierarchical breadcrumb path
function getBreadcrumbPath(pathname) {
  // Breadcrumb structure: Section > Subsection > Page
  const pathMap = {
    '/': { label: 'Dashboard', path: [] },
    '/actions': { label: 'Amendment Actions', path: [] },
    '/meetings': { label: 'Council Meetings', path: [] },
    '/calendar': { label: 'Meeting Calendar', path: [] },
    '/comments': { label: 'Public Comments', path: [] },
    '/favorites': { label: 'My Favorites', path: [] },

    // Data & Analysis section
    '/stocks': { label: 'Stock Assessments', path: ['Data & Analysis'] },
    '/ecosystem': { label: 'Ecosystem Assessment', path: ['Data & Analysis'] },
    '/timeline': { label: 'Timeline', path: ['Data & Analysis'] },
    '/compare': { label: 'Compare Actions', path: ['Data & Analysis'] },
    '/workplan': { label: 'Workplan', path: ['Data & Analysis'] },

    // SSC section
    '/ssc': { label: 'SSC Dashboard', path: ['Data & Analysis'] },
    '/ssc/members': { label: 'SSC Members', path: ['Data & Analysis', 'SSC'] },
    '/ssc/meetings': { label: 'SSC Meetings', path: ['Data & Analysis', 'SSC'] },
    '/ssc/recommendations': { label: 'SSC Recommendations', path: ['Data & Analysis', 'SSC'] },

    // CMOD section
    '/cmod': { label: 'CMOD Dashboard', path: ['Data & Analysis'] },
    '/cmod/topics': { label: 'Topics', path: ['Data & Analysis', 'CMOD'] },

    // Admin section
    '/admin/logs': { label: 'Activity Logs', path: ['Admin'] },
    '/admin/users': { label: 'User Management', path: ['Admin'] },
    '/admin/feedback': { label: 'Feedback Management', path: ['Admin'] },
    '/admin/data': { label: 'Data Management', path: ['Admin'] },
  };

  // Check for exact match
  if (pathMap[pathname]) return pathMap[pathname];

  // Handle dynamic routes
  if (pathname.startsWith('/species/')) {
    const speciesName = decodeURIComponent(pathname.split('/')[2]);
    return { label: speciesName, path: ['Data & Analysis', 'Stock Assessments'] };
  }

  if (pathname.startsWith('/cmod/workshops/')) {
    return { label: 'Workshop Details', path: ['Data & Analysis', 'CMOD'] };
  }

  // Default fallback
  return { label: 'SAFMC FMP Tracker', path: [] };
}

export default Layout;
