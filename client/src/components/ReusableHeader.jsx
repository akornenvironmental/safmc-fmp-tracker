/**
 * ReusableHeader Component
 *
 * A fully customizable header component with logo, navigation, and user controls.
 * Can be used across multiple projects with different branding and navigation needs.
 */

import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import HeaderControls from './HeaderControls';
import { useClickOutside } from '../hooks/useClickOutside';

export default function ReusableHeader({
  // Branding
  appName,
  logoSrc,
  logoAlt,
  appNameClassName = 'text-xl font-bold text-brand-blue hover:text-brand-green transition-colors whitespace-nowrap cursor-pointer',
  appSubtitle,

  // Navigation
  navLinks,
  currentPath,

  // Styling
  headerClassName = 'bg-white shadow-sm',
  containerClassName = 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
  logoContainerClassName = 'flex-shrink-0 flex items-center gap-3',
  navContainerClassName = 'hidden xl:flex xl:space-x-6',
  navLinkClassName = 'border-transparent text-gray-500 hover:border-gray-300 hover:text-brand-blue inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0',
  activeNavLinkClassName = 'border-brand-green text-brand-blue',
  mobileMenuClassName = 'xl:hidden border-t border-gray-200',

  // Feature toggles
  showLogo = true,
  showAppName = true,
  showTextSizeControl = true,
  showThemeControl = true,
  showUserMenu = true,

  // HeaderControls props
  theme,
  textSize,
  toggleTheme,
  setTextSize,
  userName,
  userEmail,
  userAvatarUrl,
  onSettingsClick,
  onLogoutClick,
  hideLogout,
  additionalMenuItems,

  // Mobile menu
  mobileMenuOpen: externalMobileMenuOpen,
  onMobileMenuToggle,
}) {
  const [internalMobileMenuOpen, setInternalMobileMenuOpen] = useState(false);
  const mobileMenuRef = useRef(null);

  const mobileMenuOpen = externalMobileMenuOpen !== undefined ? externalMobileMenuOpen : internalMobileMenuOpen;
  const setMobileMenuOpen = onMobileMenuToggle || setInternalMobileMenuOpen;

  // Close mobile menu when clicking outside or pressing Escape
  useClickOutside(mobileMenuRef, () => setMobileMenuOpen(false), mobileMenuOpen);

  const isActive = (path) => {
    if (currentPath) {
      return currentPath === path;
    }
    if (typeof window !== 'undefined') {
      return window.location.pathname === path;
    }
    return false;
  };

  return (
    <header role="banner">
      <nav role="navigation" aria-label="Primary navigation" className={headerClassName}>
        <div className={containerClassName}>
        <div className="flex justify-between items-center h-16 gap-4">
          <div className="flex items-center gap-4 min-w-0 flex-1">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="xl:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors flex-shrink-0"
              aria-label={mobileMenuOpen ? 'Close mobile menu' : 'Open mobile menu'}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>

            {/* Logo and App Name */}
            <div className={logoContainerClassName}>
              {showLogo && logoSrc && (
                <Link to="/" className="flex items-center gap-3">
                  <img
                    src={logoSrc}
                    alt={logoAlt || appName}
                    className="h-12 w-auto object-contain"
                  />
                  {showAppName && (
                    <div className="hidden lg:block">
                      <h1 className={appNameClassName}>
                        {appName}
                      </h1>
                      {appSubtitle && (
                        <p className="text-xs text-gray-500 whitespace-nowrap">{appSubtitle}</p>
                      )}
                    </div>
                  )}
                </Link>
              )}
              {!showLogo && showAppName && (
                <h1 className={appNameClassName}>
                  {appName}
                </h1>
              )}
            </div>

            {/* Desktop Navigation */}
            <div className={navContainerClassName}>
              {navLinks.map((link, index) => {
                const isActiveLink = isActive(link.to);
                const linkClasses = `${navLinkClassName} ${isActiveLink ? activeNavLinkClassName : ''}`;

                if (link.external) {
                  return (
                    <a
                      key={index}
                      href={link.to}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={linkClasses}
                    >
                      {link.icon && <span className="mr-2">{link.icon}</span>}
                      {link.label}
                    </a>
                  );
                }

                return (
                  <Link
                    key={index}
                    to={link.to}
                    className={linkClasses}
                  >
                    {link.icon && <span className="mr-2">{link.icon}</span>}
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right side controls */}
          <div className="flex items-center space-x-2 flex-shrink-0">
            <HeaderControls
              theme={theme}
              textSize={textSize}
              toggleTheme={toggleTheme}
              setTextSize={setTextSize}
              userName={userName}
              userEmail={userEmail}
              userAvatarUrl={userAvatarUrl}
              onSettingsClick={onSettingsClick}
              onLogoutClick={onLogoutClick}
              showTextSize={showTextSizeControl}
              showTheme={showThemeControl}
              showUserMenu={showUserMenu}
              hideLogout={hideLogout}
              additionalMenuItems={additionalMenuItems}
            />
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div
          id="mobile-menu"
          className={mobileMenuClassName}
        >
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navLinks.map((link, index) => {
              const isActiveLink = isActive(link.to);

              if (link.external) {
                return (
                  <a
                    key={index}
                    href={link.to}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`${
                      isActiveLink
                        ? 'bg-brand-blue text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    } block px-3 py-2 rounded-md text-base font-medium transition-colors`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {link.icon && <span className="mr-2">{link.icon}</span>}
                    {link.label}
                  </a>
                );
              }

              return (
                <Link
                  key={index}
                  to={link.to}
                  className={`${
                    isActiveLink
                      ? 'bg-brand-blue text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  } block px-3 py-2 rounded-md text-base font-medium transition-colors`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.icon && <span className="mr-2">{link.icon}</span>}
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      )}
      </nav>
    </header>
  );
}
