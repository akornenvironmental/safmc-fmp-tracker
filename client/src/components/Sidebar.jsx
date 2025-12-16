/**
 * Sidebar Component
 *
 * Left navigation sidebar with collapsible behavior.
 * Organizes navigation into logical sections.
 */

import { useState } from 'react';
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
  ChevronDown,
  GitBranch,
  FlaskConical,
  GraduationCap,
  Waves,
  Minus,
  Plus,
  RefreshCw,
} from 'lucide-react';

// Navigation item component
const NavItem = ({ item, isActive, effectiveCollapsed, isHidden, onToggleHidden }) => {
  const Icon = item.icon;

  const handleHideClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    onToggleHidden(item.to);
  };

  return (
    <Link
      to={item.to}
      className={`flex items-center justify-between pl-[10px] pr-1 h-4 rounded-md transition-all duration-200 group relative ${
        isActive
          ? 'bg-brand-blue text-white shadow-sm'
          : 'text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-brand-blue dark:hover:text-blue-400'
      }`}
      title={effectiveCollapsed ? item.label : undefined}
    >
      <div className="flex items-center min-w-0 flex-1 gap-2">
        <Icon
          className={`w-5 h-5 flex-shrink-0 ${
            isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400 group-hover:text-brand-blue dark:group-hover:text-blue-400'
          }`}
        />
        {!effectiveCollapsed && (
          <span className="text-base font-medium whitespace-nowrap truncate leading-none">{item.label}</span>
        )}
      </div>
      {!effectiveCollapsed && (
        <button
          onClick={handleHideClick}
          className={`p-0 rounded transition-colors flex-shrink-0 ml-1 -mr-[12px] w-4 h-4 flex items-center justify-center ${
            isHidden
              ? 'text-green-500 hover:text-green-600'
              : 'text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100'
          }`}
          title={isHidden ? 'Show page' : 'Hide page'}
        >
          {isHidden ? (
            <Plus className="w-4 h-4" strokeWidth={2} />
          ) : (
            <Minus className="w-4 h-4" strokeWidth={2} />
          )}
        </button>
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

// Section component with collapse functionality
const NavSection = ({ section, currentPath, effectiveCollapsed, isPageHidden, onToggleHidden, defaultExpanded = true }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const isActive = (path) => {
    if (path === '/') return currentPath === '/';
    return currentPath.startsWith(path);
  };

  // No title means main section, always shown
  const hasTitle = Boolean(section.title);

  return (
    <div className={`${hasTitle ? 'mt-4' : 'mb-0'}`}>
      {hasTitle && !effectiveCollapsed && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between pl-[10px] pr-0.5 -my-[7px] text-base font-bold text-gray-700 dark:text-gray-300 hover:bg-blue-50 hover:text-brand-blue dark:hover:bg-gray-700 dark:hover:text-blue-400 rounded transition-colors"
        >
          <span>{section.title}</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? '' : '-rotate-90'}`} />
        </button>
      )}
      {hasTitle && effectiveCollapsed && (
        <div className="h-px bg-gray-200 dark:bg-gray-700 mx-2 mb-0" />
      )}
      {(isExpanded || !hasTitle) && (
        <nav className="-space-y-[8px] mt-0">
          {section.items.map((item) => (
            <NavItem
              key={item.to}
              item={item}
              isActive={isActive(item.to)}
              effectiveCollapsed={effectiveCollapsed}
              isHidden={isPageHidden(item.to)}
              onToggleHidden={onToggleHidden}
            />
          ))}
        </nav>
      )}
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
    hiddenPages,
    toggleHiddenPage,
    isPageHidden,
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
      { to: '/ecosystem', label: 'Ecosystem', icon: Waves },
      { to: '/ssc', label: 'SSC', icon: FlaskConical },
      { to: '/cmod', label: 'CMOD Workshops', icon: GraduationCap },
      { to: '/timeline', label: 'Timeline', icon: GitBranch },
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
      ...(isAdmin ? [{ to: '/admin/data', label: 'Data Management', icon: RefreshCw }] : []),
      ...(isSuperAdmin ? [{ to: '/admin/users', label: 'User Management', icon: Users }] : []),
    ],
  } : null;

  // Build filtered sections (exclude hidden pages from original sections)
  const filteredMainNav = {
    ...mainNav,
    items: mainNav.items.filter(item => !hiddenPages.has(item.to)),
  };

  const filteredDataNav = {
    ...dataNav,
    items: dataNav.items.filter(item => !hiddenPages.has(item.to)),
  };

  const filteredAdminNav = adminNav ? {
    ...adminNav,
    items: adminNav.items.filter(item => !hiddenPages.has(item.to)),
  } : null;

  // Build hidden pages section from all navigation items
  const allNavItems = [
    ...mainNav.items,
    ...dataNav.items,
    ...(adminNav?.items || []),
  ];

  const hiddenItems = allNavItems.filter(item => hiddenPages.has(item.to));

  const hiddenNav = hiddenItems.length > 0 ? {
    title: 'Hidden',
    items: hiddenItems,
  } : null;

  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-40 flex flex-col ${
        effectiveCollapsed ? 'w-14' : 'w-52'
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center border-b border-gray-200 dark:border-gray-700 pl-[10px] pr-0.5 py-[5px] flex-shrink-0">
        <Link to="/" className="flex items-center gap-1 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center flex-shrink-0">
            <Fish className="w-5 h-5 text-white" />
          </div>
          {!effectiveCollapsed && (
            <div className="min-w-0">
              <div className="text-caption-serif text-gray-900 dark:text-white m-0 p-0" style={{ fontSize: '24px', lineHeight: '0.9', marginLeft: '2px', position: 'relative', top: '3px' }}>
                SAFMC FMP
                <br />
                <span className="text-overline-serif text-gray-500 dark:text-gray-400" style={{ fontSize: '18px' }}>
                  Tracker
                </span>
              </div>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-hidden pt-[10px] pb-0 pl-0 pr-0">
        <NavSection
          section={filteredMainNav}
          currentPath={location.pathname}
          effectiveCollapsed={effectiveCollapsed}
          isPageHidden={isPageHidden}
          onToggleHidden={toggleHiddenPage}
        />
        <NavSection
          section={filteredDataNav}
          currentPath={location.pathname}
          effectiveCollapsed={effectiveCollapsed}
          isPageHidden={isPageHidden}
          onToggleHidden={toggleHiddenPage}
        />
        {filteredAdminNav && filteredAdminNav.items.length > 0 && (
          <NavSection
            section={filteredAdminNav}
            currentPath={location.pathname}
            effectiveCollapsed={effectiveCollapsed}
            isPageHidden={isPageHidden}
            onToggleHidden={toggleHiddenPage}
          />
        )}
        {hiddenNav && (
          <NavSection
            section={hiddenNav}
            currentPath={location.pathname}
            effectiveCollapsed={effectiveCollapsed}
            isPageHidden={isPageHidden}
            onToggleHidden={toggleHiddenPage}
            defaultExpanded={false}
          />
        )}
      </div>

      {/* Spacer */}
      <div className="h-[10px] flex-shrink-0"></div>

      {/* Collapse Toggle */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-0 flex-shrink-0 mb-[10px]">
        <button
          onClick={toggleSidebar}
          className={`group flex items-center w-full pl-[10px] pr-0.5 rounded-lg text-gray-500 dark:text-gray-300 hover:bg-blue-50 hover:text-brand-blue dark:hover:bg-gray-700 dark:hover:text-white transition-colors ${
            effectiveCollapsed ? 'justify-center' : 'justify-end'
          }`}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {effectiveCollapsed ? (
            <ChevronRight className="w-4 h-4 group-hover:text-brand-blue dark:group-hover:text-white" />
          ) : (
            <div className="flex items-center gap-0.5 -translate-x-[5px]">
              <ChevronLeft className="w-4 h-4 group-hover:text-brand-blue dark:group-hover:text-white relative -top-px" />
              <span className="text-base leading-none">COLLAPSE</span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
