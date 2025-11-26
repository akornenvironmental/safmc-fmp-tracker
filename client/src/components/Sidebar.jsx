/**
 * Sidebar Component
 *
 * Left navigation sidebar with collapsible behavior.
 * Organizes navigation into logical sections.
 */

import { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useSidebar } from '../contexts/SidebarContext';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  FileText,
  Calendar,
  MessageSquare,
  Fish,
  GitCompare,
  ClipboardList,
  Activity,
  Users,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  User,
  Settings,
  Shield,
  LogOut,
} from 'lucide-react';

// Navigation item component
const NavItem = ({ item, isActive, effectiveCollapsed }) => {
  const Icon = item.icon;

  return (
    <Link
      to={item.to}
      className={`flex items-center px-3 py-2.5 rounded-lg transition-all duration-200 group relative ${
        isActive
          ? 'bg-brand-blue text-white shadow-md'
          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
      }`}
      title={effectiveCollapsed ? item.label : undefined}
    >
      <Icon
        className={`w-5 h-5 flex-shrink-0 ${
          isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400 group-hover:text-brand-blue dark:group-hover:text-blue-400'
        }`}
      />
      {!effectiveCollapsed && (
        <span className="ml-3 text-sm font-medium whitespace-nowrap">{item.label}</span>
      )}
      {/* Tooltip for collapsed state */}
      {effectiveCollapsed && (
        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
          {item.label}
        </div>
      )}
    </Link>
  );
};

// Section component
const NavSection = ({ section, currentPath, effectiveCollapsed }) => {
  const isActive = (path) => {
    if (path === '/') return currentPath === '/';
    return currentPath.startsWith(path);
  };

  return (
    <div className="mb-4">
      {section.title && !effectiveCollapsed && (
        <h3 className="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          {section.title}
        </h3>
      )}
      {section.title && effectiveCollapsed && (
        <div className="h-px bg-gray-200 dark:bg-gray-700 mx-3 mb-2" />
      )}
      <nav className="space-y-1">
        {section.items.map((item) => (
          <NavItem
            key={item.to}
            item={item}
            isActive={isActive(item.to)}
            effectiveCollapsed={effectiveCollapsed}
          />
        ))}
      </nav>
    </div>
  );
};

const Sidebar = ({ user }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const {
    effectiveCollapsed,
    toggleSidebar,
    handleMouseEnter,
    handleMouseLeave,
    isCollapsed,
  } = useSidebar();
  const { logout } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const profileMenuRef = useRef(null);

  const isSuperAdmin = user?.role === 'super_admin';
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';

  const handleLogout = async () => {
    setShowProfileMenu(false);
    await logout();
    navigate('/login');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Main navigation items
  const mainNav = {
    items: [
      { to: '/', label: 'Dashboard', icon: LayoutDashboard },
      { to: '/actions', label: 'Actions', icon: FileText },
      { to: '/meetings', label: 'Meetings', icon: Calendar },
      { to: '/comments', label: 'Comments', icon: MessageSquare },
    ],
  };

  // Data & Analysis section
  const dataNav = {
    title: 'Data & Analysis',
    items: [
      { to: '/stocks', label: 'Stock Assessments', icon: Fish },
      { to: '/compare', label: 'Compare Actions', icon: GitCompare },
      { to: '/workplan', label: 'Workplan', icon: ClipboardList },
    ],
  };

  // Admin section (only for admins)
  const adminNav = isAdmin ? {
    title: 'Admin',
    items: [
      ...(isAdmin ? [{ to: '/admin/logs', label: 'Activity Logs', icon: Activity }] : []),
      ...(isAdmin ? [{ to: '/admin/feedback', label: 'Feedback', icon: MessageSquare }] : []),
      ...(isSuperAdmin ? [{ to: '/admin/users', label: 'User Management', icon: Users }] : []),
    ],
  } : null;

  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-40 flex flex-col ${
        effectiveCollapsed ? 'w-14' : 'w-48'
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Logo Section */}
      <div className="h-14 flex items-center border-b border-gray-200 dark:border-gray-700 px-2 flex-shrink-0">
        <Link to="/" className="flex items-center gap-2 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center flex-shrink-0">
            <Fish className="w-5 h-5 text-white" />
          </div>
          {!effectiveCollapsed && (
            <div className="min-w-0">
              <h1 className="text-sm font-bold text-gray-900 dark:text-white truncate leading-tight">
                SAFMC FMP
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate leading-tight">
                Tracker
              </p>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto py-3 px-1.5">
        <NavSection section={mainNav} currentPath={location.pathname} effectiveCollapsed={effectiveCollapsed} />
        <NavSection section={dataNav} currentPath={location.pathname} effectiveCollapsed={effectiveCollapsed} />
        {adminNav && adminNav.items.length > 0 && (
          <NavSection section={adminNav} currentPath={location.pathname} effectiveCollapsed={effectiveCollapsed} />
        )}
      </div>

      {/* User Profile Section */}
      {user && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-1.5 flex-shrink-0" ref={profileMenuRef}>
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className={`flex items-center w-full px-2 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
              effectiveCollapsed ? 'justify-center' : 'gap-2'
            }`}
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center text-white text-xs font-medium flex-shrink-0">
              {(user.name || user.email || '?').charAt(0).toUpperCase()}
            </div>
            {!effectiveCollapsed && (
              <>
                <span className="text-xs font-medium text-gray-900 dark:text-white truncate flex-1 text-left">
                  {user.name || user.email}
                </span>
                <ChevronDown className={`w-3.5 h-3.5 text-gray-500 transition-transform flex-shrink-0 ${showProfileMenu ? 'rotate-180' : ''}`} />
              </>
            )}
          </button>

          {/* Profile Dropdown Menu */}
          {showProfileMenu && (
            <div className={`absolute ${effectiveCollapsed ? 'left-14' : 'left-1.5 right-1.5'} bottom-12 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50`}>
              {/* User info header */}
              <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-900 dark:text-white">{user.name || 'User'}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                {user.role && (
                  <span className="inline-block mt-1 px-1.5 py-0.5 text-xs font-medium bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20 dark:text-blue-300 rounded">
                    {user.role.replace('_', ' ')}
                  </span>
                )}
              </div>

              {/* Menu items */}
              <div className="py-1">
                <Link
                  to="/profile"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <User className="w-3.5 h-3.5" />
                  My Profile
                </Link>
                <Link
                  to="/preferences"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Settings className="w-3.5 h-3.5" />
                  Preferences
                </Link>
                <Link
                  to="/security"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Shield className="w-3.5 h-3.5" />
                  Security
                </Link>
              </div>

              {/* Admin section */}
              {isSuperAdmin && (
                <div className="border-t border-gray-200 dark:border-gray-700 py-1">
                  <Link
                    to="/admin/users"
                    onClick={() => setShowProfileMenu(false)}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Users className="w-3.5 h-3.5" />
                    User Management
                  </Link>
                </div>
              )}

              {/* Sign out */}
              <div className="border-t border-gray-200 dark:border-gray-700 py-1">
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Collapse Toggle */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-1.5 flex-shrink-0">
        <button
          onClick={toggleSidebar}
          className={`flex items-center w-full px-2 py-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
            effectiveCollapsed ? 'justify-center' : ''
          }`}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {effectiveCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span className="ml-1.5 text-xs">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
