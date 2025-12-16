import { Outlet, useLocation, Link, useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { useSidebar } from '../contexts/SidebarContext';
import Sidebar from './Sidebar';
import AIAssistant from './AIAssistant';
import FeedbackButton from './FeedbackButton';
import Footer from './Footer';
import {
  Sun, Moon, Type, Fish, ChevronRight, LayoutDashboard, FileText,
  Calendar, MessageSquare, GitCompare, ClipboardList, Activity,
  Users, GitBranch, FlaskConical, GraduationCap, Waves, RefreshCw,
  Shield, LogOut
} from 'lucide-react';

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme, textSize, setTextSize } = useTheme();
  const { user, logout } = useAuth();
  const { effectiveCollapsed } = useSidebar();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef(null);

  const cycleTextSize = () => {
    const sizes = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(textSize);
    const nextIndex = (currentIndex + 1) % sizes.length;
    setTextSize(sizes[nextIndex]);
  };

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Get user initials (first and last)
  const getUserInitials = () => {
    if (!user) return '?';

    // Try to get initials from name first
    if (user.name) {
      const nameParts = user.name.trim().split(/\s+/);
      if (nameParts.length >= 2) {
        return (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase();
      }
      return nameParts[0].charAt(0).toUpperCase();
    }

    // Fallback to email
    if (user.email) {
      return user.email.charAt(0).toUpperCase();
    }

    return '?';
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
              const Icon = breadcrumb.icon;

              return (
                <>
                  {/* Path segments */}
                  {breadcrumb.path.map((segment, index) => (
                    <div key={index} className="flex items-center gap-2 flex-shrink-0">
                      {index > 0 && <ChevronRight className="w-4 h-4 text-gray-400" />}
                      <span className="font-heading text-gray-900 dark:text-white leading-none" style={{ fontSize: '24px', position: 'relative', top: '4px', margin: '0', padding: '0' }}>
                        {segment}
                      </span>
                    </div>
                  ))}
                  {breadcrumb.path.length > 0 && <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />}

                  {/* Page icon */}
                  <Icon className="w-5 h-5 text-brand-blue flex-shrink-0" style={{ position: 'relative', top: '4px' }} />

                  {/* Page title */}
                  <h1 className="font-heading text-gray-900 dark:text-white truncate mb-0 leading-none" style={{ fontSize: '24px', position: 'relative', top: '4px', margin: '0', padding: '0' }}>
                    {breadcrumb.label}
                  </h1>
                </>
              );
            })()}
          </div>

          {/* Theme Controls & User Menu */}
          <div className="flex items-center gap-1 flex-shrink-0">
            {/* Text Size Toggle */}
            <button
              onClick={cycleTextSize}
              className="flex items-center justify-center w-10 h-10 text-gray-500 hover:text-brand-blue hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title={`Text size: ${textSize} (click to cycle)`}
              aria-label={`Text size: ${textSize}. Click to cycle through sizes.`}
            >
              <Type className="w-5 h-5" />
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              className="flex items-center justify-center w-10 h-10 text-gray-500 hover:text-brand-blue hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
              aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
            </button>

            {/* Pipe Delimiter */}
            {user && (
              <div className="h-7 w-px bg-gray-300 dark:bg-gray-600 mx-1"></div>
            )}

            {/* User Profile Menu */}
            {user && (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-brand-blue to-blue-600 text-white text-base font-medium hover:shadow-md transition-shadow"
                  title="User menu"
                  aria-label="User menu"
                >
                  {getUserInitials()}
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50">
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                      <p className="text-xs text-gray-600 dark:text-gray-400">Signed in as</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate mt-1">
                        {user.email}
                      </p>
                      {user.name && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                          {user.name}
                        </p>
                      )}
                      {(user.role === 'admin' || user.role === 'super_admin') && (
                        <span className="inline-flex items-center gap-1 mt-2 text-xs text-purple-600 dark:text-purple-400">
                          <Shield className="w-3 h-3" />
                          {user.role === 'super_admin' ? 'Super Admin' : 'Admin'}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-4 py-3 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors gap-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign out</span>
                    </button>
                  </div>
                )}
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
    '/': { label: 'Dashboard', path: [], icon: LayoutDashboard },
    '/actions': { label: 'Actions', path: [], icon: FileText },
    '/meetings': { label: 'Council Meetings', path: [], icon: Calendar },
    '/calendar': { label: 'Meeting Calendar', path: [], icon: Calendar },
    '/comments': { label: 'Public Comments', path: [], icon: MessageSquare },
    '/favorites': { label: 'My Favorites', path: [], icon: MessageSquare },

    // Data & Analysis section
    '/stocks': { label: 'Stock Assessments', path: ['Data & Analysis'], icon: Fish },
    '/ecosystem': { label: 'Ecosystem Assessment', path: ['Data & Analysis'], icon: Waves },
    '/timeline': { label: 'Timeline', path: ['Data & Analysis'], icon: GitBranch },
    '/compare': { label: 'Compare Actions', path: ['Data & Analysis'], icon: GitCompare },
    '/workplan': { label: 'Workplan', path: ['Data & Analysis'], icon: ClipboardList },

    // SSC section
    '/ssc': { label: 'SSC Dashboard', path: ['Data & Analysis'], icon: FlaskConical },
    '/ssc/members': { label: 'SSC Members', path: ['Data & Analysis', 'SSC'], icon: Users },
    '/ssc/meetings': { label: 'SSC Meetings', path: ['Data & Analysis', 'SSC'], icon: Calendar },
    '/ssc/recommendations': { label: 'SSC Recommendations', path: ['Data & Analysis', 'SSC'], icon: FileText },

    // CMOD section
    '/cmod': { label: 'CMOD Dashboard', path: ['Data & Analysis'], icon: GraduationCap },
    '/cmod/topics': { label: 'Topics', path: ['Data & Analysis', 'CMOD'], icon: FileText },

    // Admin section
    '/admin/logs': { label: 'Activity Logs', path: ['Admin'], icon: Activity },
    '/admin/users': { label: 'User Management', path: ['Admin'], icon: Users },
    '/admin/feedback': { label: 'Feedback Management', path: ['Admin'], icon: MessageSquare },
    '/admin/data': { label: 'Data Management', path: ['Admin'], icon: RefreshCw },
  };

  // Check for exact match
  if (pathMap[pathname]) return pathMap[pathname];

  // Handle dynamic routes with security validation
  if (pathname.startsWith('/species/')) {
    try {
      const speciesName = decodeURIComponent(pathname.split('/')[2]);
      // Limit length to prevent UI issues and validate it's a reasonable string
      if (speciesName && speciesName.length < 100 && speciesName.length > 0) {
        return { label: speciesName, path: ['Data & Analysis', 'Stock Assessments'], icon: Fish };
      }
    } catch (error) {
      console.error('Invalid species name in URL:', error);
    }
    return { label: 'Stock Assessments', path: ['Data & Analysis'], icon: Fish };
  }

  if (pathname.startsWith('/cmod/workshops/')) {
    return { label: 'Workshop Details', path: ['Data & Analysis', 'CMOD'], icon: GraduationCap };
  }

  // Default fallback
  return { label: 'SAFMC FMP Tracker', path: [], icon: LayoutDashboard };
}

export default Layout;
