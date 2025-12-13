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
  GitBranch,
  Settings,
  Shield,
  LogOut,
  FlaskConical,
  GraduationCap,
  Heart,
  Waves,
  Star,
  RefreshCw,
} from 'lucide-react';

// Navigation item component
const NavItem = ({ item, isActive, effectiveCollapsed, isFavorited, onToggleFavorite }) => {
  const Icon = item.icon;

  const handleFavoriteClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    onToggleFavorite(item.to);
  };

  return (
    <Link
      to={item.to}
      className={`flex items-center justify-between pl-[15px] pr-0 -my-[9px] rounded-md transition-all duration-200 group relative ${
        isActive
          ? 'bg-brand-blue text-white shadow-sm'
          : 'text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-brand-blue dark:hover:text-blue-400'
      }`}
      title={effectiveCollapsed ? item.label : undefined}
    >
      <div className="flex items-center min-w-0 flex-1">
        <Icon
          className={`w-5 h-5 flex-shrink-0 ${
            isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400 group-hover:text-brand-blue dark:group-hover:text-blue-400'
          }`}
        />
        {!effectiveCollapsed && (
          <span className="ml-1 text-base font-medium whitespace-nowrap truncate">{item.label}</span>
        )}
      </div>
      {!effectiveCollapsed && (
        <button
          onClick={handleFavoriteClick}
          className={`p-0 rounded transition-colors flex-shrink-0 ml-2 -mr-[23px] ${
            isFavorited
              ? 'text-yellow-500 hover:text-yellow-600'
              : 'text-gray-400 hover:text-yellow-500 opacity-0 group-hover:opacity-100'
          }`}
          title={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
        >
          <Star
            className="w-4 h-4"
            fill={isFavorited ? 'currentColor' : 'none'}
            strokeWidth={2}
          />
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
const NavSection = ({ section, currentPath, effectiveCollapsed, isNavFavorited, onToggleFavorite }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const isActive = (path) => {
    if (path === '/') return currentPath === '/';
    return currentPath.startsWith(path);
  };

  // No title means main section, always shown
  const hasTitle = Boolean(section.title);

  return (
    <div className="mb-0">
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
        <nav className="space-y-0 mt-0">
          {section.items.map((item) => (
            <NavItem
              key={item.to}
              item={item}
              isActive={isActive(item.to)}
              effectiveCollapsed={effectiveCollapsed}
              isFavorited={isNavFavorited(item.to)}
              onToggleFavorite={onToggleFavorite}
            />
          ))}
        </nav>
      )}
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
    isNavFavorited,
    toggleNavFavorite,
    navFavorites,
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

  // Build favorites section from all navigation items
  const allNavItems = [
    ...mainNav.items,
    ...dataNav.items,
    ...(adminNav?.items || []),
  ];

  const favoriteItems = allNavItems.filter(item => navFavorites.has(item.to));

  const favoritesNav = favoriteItems.length > 0 ? {
    title: 'Favorites',
    items: favoriteItems,
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
              <h1 className="text-base font-bold text-gray-900 dark:text-white truncate leading-tight">
                SAFMC FMP
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate leading-tight">
                Tracker
              </p>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-hidden pt-[10px] pb-0 pl-0 pr-0">
        <NavSection
          section={mainNav}
          currentPath={location.pathname}
          effectiveCollapsed={effectiveCollapsed}
          isNavFavorited={isNavFavorited}
          onToggleFavorite={toggleNavFavorite}
        />
        <NavSection
          section={dataNav}
          currentPath={location.pathname}
          effectiveCollapsed={effectiveCollapsed}
          isNavFavorited={isNavFavorited}
          onToggleFavorite={toggleNavFavorite}
        />
        {adminNav && adminNav.items.length > 0 && (
          <NavSection
            section={adminNav}
            currentPath={location.pathname}
            effectiveCollapsed={effectiveCollapsed}
            isNavFavorited={isNavFavorited}
            onToggleFavorite={toggleNavFavorite}
          />
        )}
      </div>

      {/* User Profile Section */}
      {user && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-0 flex-shrink-0" ref={profileMenuRef}>
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className={`flex items-center w-full pl-[10px] pr-0.5 py-[5px] rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
              effectiveCollapsed ? 'justify-center' : 'gap-1'
            }`}
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
              {(user.name || user.email || '?').charAt(0).toUpperCase()}
            </div>
            {!effectiveCollapsed && (
              <>
                <span className="text-sm font-medium text-gray-900 dark:text-white truncate flex-1 text-left">
                  {user.name || user.email}
                </span>
                <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform flex-shrink-0 ${showProfileMenu ? 'rotate-180' : ''}`} />
              </>
            )}
          </button>

          {/* Profile Dropdown Menu */}
          {showProfileMenu && (
            <div className={`absolute ${effectiveCollapsed ? 'left-14' : 'left-1.5 right-1.5'} bottom-12 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50`}>
              {/* User info header */}
              <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user.name || 'User'}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                {user.role && (
                  <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20 dark:text-blue-300 rounded">
                    {user.role.replace('_', ' ')}
                  </span>
                )}
              </div>

              {/* Menu items */}
              <div className="py-1">
                <Link
                  to="/profile"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <User className="w-4 h-4" />
                  My Profile
                </Link>
                <Link
                  to="/preferences"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Settings className="w-4 h-4" />
                  Preferences
                </Link>
                <Link
                  to="/security"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Shield className="w-4 h-4" />
                  Security
                </Link>
              </div>

              {/* Admin section */}
              {isSuperAdmin && (
                <div className="border-t border-gray-200 dark:border-gray-700 py-1">
                  <Link
                    to="/admin/users"
                    onClick={() => setShowProfileMenu(false)}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Users className="w-4 h-4" />
                    User Management
                  </Link>
                </div>
              )}

              {/* Sign out */}
              <div className="border-t border-gray-200 dark:border-gray-700 py-1">
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full px-3 py-1.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Collapse Toggle */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-0 flex-shrink-0">
        <button
          onClick={toggleSidebar}
          className={`flex items-center w-full pl-[10px] pr-0.5 -my-[3px] rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
            effectiveCollapsed ? 'justify-center' : ''
          }`}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {effectiveCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span className="ml-0.5 text-base">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
