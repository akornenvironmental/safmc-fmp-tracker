/**
 * HeaderControls Component
 *
 * Reusable component for header controls including:
 * - Text size cycling (small, medium, large)
 * - Theme toggle (light/dark)
 * - User menu with dropdown
 */

import { useState, useEffect } from 'react';
import { Sun, Moon, Type, User, Settings as SettingsIcon, LogOut } from 'lucide-react';

export default function HeaderControls({
  theme,
  toggleTheme,
  textSize,
  setTextSize,
  userName = 'User',
  userEmail,
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

  const cycleTextSize = () => {
    const sizes = ['small', 'medium', 'large'];
    const currentIndex = sizes.indexOf(textSize);
    const nextIndex = (currentIndex + 1) % sizes.length;
    setTextSize(sizes[nextIndex]);
  };

  const toggleUserMenu = () => setShowUserDropdown(!showUserDropdown);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      const target = event.target;
      if (showUserDropdown && !target.closest('.user-menu-container')) {
        setShowUserDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserDropdown]);

  return (
    <div className="flex items-center space-x-2">
      {/* Text Size Toggle */}
      {showTextSize && (
        <button
          onClick={cycleTextSize}
          className="flex items-center justify-center w-9 h-9 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          title={`Text size: ${textSize} (click to cycle)`}
        >
          <Type className="w-4 h-4" />
        </button>
      )}

      {/* Dark Mode Toggle */}
      {showTheme && (
        <button
          onClick={toggleTheme}
          className="flex items-center justify-center w-9 h-9 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
        </button>
      )}

      {/* User Menu */}
      {showUserMenu && (
        <div className="relative user-menu-container border-l border-white/20 pl-4 ml-2">
          <button
            onClick={toggleUserMenu}
            className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-brand-blue to-blue-600 text-white hover:shadow-md transition-all duration-200 hover:-translate-y-0.5"
            title="User Menu"
          >
            {userAvatarUrl ? (
              <img
                src={userAvatarUrl}
                alt={userName}
                className="w-full h-full rounded-lg object-cover"
              />
            ) : (
              <User className="w-5 h-5" />
            )}
          </button>

          {/* Dropdown Menu */}
          {showUserDropdown && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50">
              {/* User Info Header */}
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div className="font-semibold text-brand-blue dark:text-white text-sm mb-1">
                  {userName}
                </div>
                {userEmail && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {userEmail}
                  </div>
                )}
              </div>

              {/* Menu Items */}
              <div className="py-1">
                {/* Settings */}
                {onSettingsClick && (
                  <button
                    onClick={() => {
                      onSettingsClick();
                      setShowUserDropdown(false);
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <SettingsIcon className="w-4 h-4" />
                    Settings
                  </button>
                )}

                {/* Additional Menu Items */}
                {additionalMenuItems.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      item.onClick();
                      setShowUserDropdown(false);
                    }}
                    className={item.className || "w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"}
                  >
                    {item.icon && <span className="w-4 h-4">{item.icon}</span>}
                    {item.label}
                  </button>
                ))}

                {/* Logout */}
                {!hideLogout && onLogoutClick && (
                  <>
                    <div className="border-t border-gray-200 dark:border-gray-700 my-1" />
                    <button
                      onClick={() => {
                        onLogoutClick();
                        setShowUserDropdown(false);
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
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
