import { Outlet, Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { Type, Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import Footer from './Footer';

const Layout = () => {
  const location = useLocation();
  const { theme, toggleTheme, textSize, cycleTextSize, isDark } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <nav className="bg-white shadow-sm">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16 gap-4">
            <div className="flex items-center gap-4 min-w-0 flex-1">
              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors flex-shrink-0"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                )}
              </button>

              <div className="flex-shrink-0 flex items-center gap-3">
                <Link to="/" className="flex items-center gap-3">
                  <div>
                    <h1 className="text-xl font-bold text-brand-blue cursor-pointer hover:text-brand-green transition-colors whitespace-nowrap">
                      SAFMC FMP Tracker
                    </h1>
                    <p className="text-xs text-gray-500 whitespace-nowrap hidden sm:block">Fishery Management Plans • Meetings • Comments</p>
                  </div>
                </Link>
              </div>

              {/* Desktop navigation */}
              <div className="hidden md:flex md:space-x-6">
                <Link
                  to="/"
                  className={`${
                    location.pathname === '/'
                      ? 'border-brand-green text-brand-blue'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-brand-blue'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/actions"
                  className={`${
                    location.pathname === '/actions'
                      ? 'border-brand-green text-brand-blue'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-brand-blue'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0`}
                >
                  Actions
                </Link>
                <Link
                  to="/meetings"
                  className={`${
                    location.pathname === '/meetings'
                      ? 'border-brand-green text-brand-blue'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-brand-blue'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0`}
                >
                  Meetings
                </Link>
                <Link
                  to="/comments"
                  className={`${
                    location.pathname === '/comments'
                      ? 'border-brand-green text-brand-blue'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-brand-blue'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0`}
                >
                  Comments
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-2 flex-shrink-0">
              {/* Text Size Toggle */}
              <button
                onClick={cycleTextSize}
                className="flex items-center justify-center w-9 h-9 text-gray-500 hover:text-brand-blue hover:bg-gray-100 rounded-lg transition-colors"
                title={`Text size: ${textSize} (click to cycle)`}
              >
                <Type className="w-4 h-4" />
              </button>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="flex items-center justify-center w-9 h-9 text-gray-500 hover:text-brand-blue hover:bg-gray-100 rounded-lg transition-colors"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Mobile menu dropdown */}
          {mobileMenuOpen && (
            <div className="md:hidden border-t border-gray-200">
              <div className="px-2 pt-2 pb-3 space-y-1">
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`${
                    location.pathname === '/'
                      ? 'bg-brand-blue text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  } block px-3 py-2 rounded-md text-base font-medium transition-colors`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/actions"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`${
                    location.pathname === '/actions'
                      ? 'bg-brand-blue text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  } block px-3 py-2 rounded-md text-base font-medium transition-colors`}
                >
                  Actions
                </Link>
                <Link
                  to="/meetings"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`${
                    location.pathname === '/meetings'
                      ? 'bg-brand-blue text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  } block px-3 py-2 rounded-md text-base font-medium transition-colors`}
                >
                  Meetings
                </Link>
                <Link
                  to="/comments"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`${
                    location.pathname === '/comments'
                      ? 'bg-brand-blue text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  } block px-3 py-2 rounded-md text-base font-medium transition-colors`}
                >
                  Comments
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto py-6 sm:px-6 lg:px-8 flex-grow w-full">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
};

export default Layout;
