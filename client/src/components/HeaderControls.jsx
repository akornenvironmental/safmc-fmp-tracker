/**
 * HeaderControls Component
 *
 * Reusable component for header controls including:
 * - Text size cycling (small, medium, large)
 * - Theme toggle (light/dark)
 * - User menu with dropdown
 */

import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Sun, Moon, Type, User, Settings as SettingsIcon, LogOut, Users } from 'lucide-react';
import { useClickOutside } from '../hooks/useClickOutside';

export default function HeaderControls({
  theme,
  toggleTheme,
  textSize,
  setTextSize,
  userName = 'User',
  userEmail,
  userRole,
  userAvatarUrl,
  onSettingsClick,
  onLogoutClick,
  showTextSize = true,
  showTheme = true,
  showUserMenu = true,
  hideLogout = false,
  additionalMenuItems = []
}) {
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const userMenuRef = useRef(null);

  const cycleTextSize = () => {
    const sizes = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(textSize);
    const nextIndex = (currentIndex + 1) % sizes.length;
    setTextSize(sizes[nextIndex]);
  };

  const toggleUserMenu = () => setShowUserDropdown(!showUserDropdown);

  // Close dropdown when clicking outside or pressing Escape
  useClickOutside(userMenuRef, () => setShowUserDropdown(false), showUserDropdown);

  return (
    <div className="flex items-center space-x-1">
      {/* Text Size Toggle */}
      {showTextSize && (
        <button
          onClick={cycleTextSize}
          className="flex items-center justify-center w-9 h-9 text-gray-500 hover:text-brand-blue hover:bg-gray-100 rounded-lg transition-colors"
          title={`Text size: ${textSize} (click to cycle)`}
          aria-label={`Text size: ${textSize}. Click to cycle through sizes.`}
        >
          <Type className="w-4 h-4" aria-hidden="true" />
        </button>
      )}

      {/* Dark Mode Toggle */}
      {showTheme && (
        <button
          onClick={toggleTheme}
          className="flex items-center justify-center w-9 h-9 text-gray-500 hover:text-brand-blue hover:bg-gray-100 rounded-lg transition-colors"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === 'light' ? <Moon className="w-4 h-4" aria-hidden="true" /> : <Sun className="w-4 h-4" aria-hidden="true" />}
        </button>
      )}

      {/* User Menu */}
      {showUserMenu && (
        <div ref={userMenuRef} className="relative user-menu-container border-l border-gray-300 pl-2 ml-1">
          <button
            onClick={toggleUserMenu}
            className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-brand-blue to-blue-600 text-white hover:shadow-md transition-all duration-200 hover:-translate-y-0.5"
            title="User Menu"
            aria-label="User menu"
            aria-expanded={showUserDropdown}
            aria-haspopup="true"
          >
            {userAvatarUrl ? (
              <img
                src={userAvatarUrl}
                alt={userName}
                className="w-full h-full rounded-lg object-cover"
              />
            ) : (
              <User className="w-5 h-5" aria-hidden="true" />
            )}
          </button>

          {/* Dropdown Menu */}
          {showUserDropdown && (
            <div
              role="menu"
              aria-label="User menu options"
              className="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
            >
              {/* User Info Header */}
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div className="font-semibold text-brand-blue dark:text-white text-sm mb-1">
                  {userName}
                </div>
                {userEmail && (
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    {userEmail}
                  </div>
                )}
                {userRole && (
                  <div className="mt-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        userRole === 'super_admin'
                          ? 'bg-purple-700 text-white dark:bg-purple-600 dark:text-white'
                          : userRole === 'admin'
                          ? 'bg-blue-700 text-white dark:bg-blue-600 dark:text-white'
                          : 'bg-gray-600 text-white dark:bg-gray-500 dark:text-white'
                      }`}
                    >
                      {userRole === 'super_admin'
                        ? 'Super Admin'
                        : userRole === 'admin'
                        ? 'Admin'
                        : 'Editor'}
                    </span>
                  </div>
                )}
              </div>

              {/* Menu Items */}
              <div className="py-1">
                {/* Settings */}
                {onSettingsClick && (
                  <button
                    role="menuitem"
                    onClick={() => {
                      onSettingsClick();
                      setShowUserDropdown(false);
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <SettingsIcon className="w-4 h-4" aria-hidden="true" />
                    Settings
                  </button>
                )}

                {/* Additional Menu Items */}
                {additionalMenuItems.map((item, index) => {
                  // Handle dividers
                  if (item.type === 'divider') {
                    return <div key={index} className="border-t border-gray-200 dark:border-gray-700 my-1" role="separator" />;
                  }

                  // Get icon component
                  const IconComponent = item.icon === 'users' ? Users : null;

                  // Handle link items
                  if (item.to) {
                    return (
                      <Link
                        key={index}
                        to={item.to}
                        role="menuitem"
                        onClick={() => setShowUserDropdown(false)}
                        className={item.className || "w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"}
                      >
                        {IconComponent && <IconComponent className="w-4 h-4" aria-hidden="true" />}
                        {item.label}
                      </Link>
                    );
                  }

                  // Handle button items with onClick
                  return (
                    <button
                      key={index}
                      role="menuitem"
                      onClick={() => {
                        item.onClick?.();
                        setShowUserDropdown(false);
                      }}
                      className={item.className || "w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"}
                    >
                      {IconComponent && <IconComponent className="w-4 h-4" aria-hidden="true" />}
                      {item.label}
                    </button>
                  );
                })}

                {/* Logout */}
                {!hideLogout && onLogoutClick && (
                  <>
                    <div className="border-t border-gray-200 dark:border-gray-700 my-1" role="separator" />
                    <button
                      role="menuitem"
                      onClick={() => {
                        onLogoutClick();
                        setShowUserDropdown(false);
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
                      <LogOut className="w-4 h-4" aria-hidden="true" />
                      Sign Out
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
