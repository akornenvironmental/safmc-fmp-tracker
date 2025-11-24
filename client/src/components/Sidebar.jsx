/**
 * Sidebar Component
 *
 * Left navigation sidebar with collapsible behavior.
 * Organizes navigation into logical sections.
 */

import { Link, useLocation } from 'react-router-dom';
import { useSidebar } from '../contexts/SidebarContext';
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
  const {
    effectiveCollapsed,
    toggleSidebar,
    handleMouseEnter,
    handleMouseLeave,
    isCollapsed,
  } = useSidebar();

  const isSuperAdmin = user?.role === 'super_admin';
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin';

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
      ...(isSuperAdmin ? [{ to: '/admin/users', label: 'User Management', icon: Users }] : []),
    ],
  } : null;

  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-40 flex flex-col ${
        effectiveCollapsed ? 'w-16' : 'w-64'
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center border-b border-gray-200 dark:border-gray-700 px-3 flex-shrink-0">
        <Link to="/" className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center flex-shrink-0">
            <Fish className="w-6 h-6 text-white" />
          </div>
          {!effectiveCollapsed && (
            <div className="min-w-0">
              <h1 className="text-sm font-bold text-brand-blue dark:text-white truncate">
                SAFMC FMP
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                Tracker
              </p>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto py-4 px-2">
        <NavSection section={mainNav} currentPath={location.pathname} effectiveCollapsed={effectiveCollapsed} />
        <NavSection section={dataNav} currentPath={location.pathname} effectiveCollapsed={effectiveCollapsed} />
        {adminNav && adminNav.items.length > 0 && (
          <NavSection section={adminNav} currentPath={location.pathname} effectiveCollapsed={effectiveCollapsed} />
        )}
      </div>

      {/* Collapse Toggle */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-2 flex-shrink-0">
        <button
          onClick={toggleSidebar}
          className={`flex items-center w-full px-3 py-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
            effectiveCollapsed ? 'justify-center' : ''
          }`}
          title={isCollapsed ? 'Expand sidebar ([ or Cmd+\\)' : 'Collapse sidebar ([ or Cmd+\\)'}
        >
          {effectiveCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <ChevronLeft className="w-5 h-5" />
              <span className="ml-2 text-xs">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
