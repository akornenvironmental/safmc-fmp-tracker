import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import ReusableHeader from './ReusableHeader';
import ReusableFooter from './ReusableFooter';
import AIAssistant from './AIAssistant';
import safmcLogo from '../assets/safmc-logo.jpg';

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme, textSize, setTextSize, isDark } = useTheme();
  const { user, logout, isSuperAdmin, isAdmin } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Build navigation links based on user role
  const navLinks = [
    { to: '/', label: 'Dashboard' },
    { to: '/actions', label: 'Actions' },
    { to: '/meetings', label: 'Meetings' },
    { to: '/comments', label: 'Comments' },
    { to: '/stocks', label: 'Stocks' },
    { to: '/compare', label: 'Compare' },
    { to: '/workplan', label: 'Workplan' },
    // Admin links - conditionally shown based on role
    ...(isAdmin() ? [{ to: '/admin/logs', label: 'Activity Logs' }] : []),
    ...(isSuperAdmin() ? [{ to: '/admin/users', label: 'Users' }] : [])
  ];

  const customDescription = (
    <>
      <strong className="text-white">Fishery Management Plan Tracking System.</strong> This system tracks amendments, meetings, and public comments for South Atlantic FMPs. All data is sourced from publicly available information on SAFMC.net.
    </>
  );

  const featureBadges = [
    {
      icon: (
        <svg className="w-4 h-4 text-brand-green" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      ),
      label: 'Public Data'
    }
  ];

  const customFooterContent = null;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col">
      {/* Skip Navigation Links for 508 Compliance */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#footer" className="skip-link">
        Skip to footer
      </a>

      <ReusableHeader
        appName="SAFMC FMP Tracker"
        appSubtitle="Fishery Management Plan Development Tracking"
        logoSrc={safmcLogo}
        logoAlt="SAFMC Logo"
        navLinks={navLinks}
        currentPath={location.pathname}
        theme={theme}
        textSize={textSize}
        toggleTheme={toggleTheme}
        setTextSize={setTextSize}
        userName={user?.name || user?.email}
        userEmail={user?.email}
        userRole={user?.role}
        onLogoutClick={handleLogout}
        headerClassName="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50"
        containerClassName="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8"
      />

      <main
        id="main-content"
        role="main"
        aria-label="Main content"
        className="max-w-[1600px] mx-auto py-6 sm:px-6 lg:px-8 flex-grow w-full"
      >
        <Outlet />
      </main>

      <ReusableFooter
        appName="SAFMC FMP Tracker"
        version="1.0.0"
        companyName="akorn environmental consulting, LLC"
        companyUrl="https://akornenvironmental.com/"
        description={(
          <>
            <strong className="text-white">Fishery Management Plan Tracking System.</strong> This system tracks amendments, meetings, public comments, and stock assessments for South Atlantic FMPs. All data is sourced from publicly available information on SAFMC.net, SEDAR, and NOAA sources.
          </>
        )}
        aiNotice="This system uses AI-powered tools to assist with data analysis and summarization. All AI-generated information should be reviewed for accuracy and verified against official SAFMC sources."
        contactEmail="aaron.kornbluth@gmail.com"
        contactSubject="SAFMC FMP Tracker Feedback"
        featureBadges={featureBadges}
        showAIPoweredBadge={false}
        customContent={(
          <div className="text-xs text-blue-100 pb-2 border-b border-blue-300/30">
            <strong>Desktop optimized</strong> • Authorized users only • This system contains fishery management data collected from public sources for research and tracking purposes.
          </div>
        )}
        footerLinks={[
          { to: '/privacy', label: 'Privacy' },
          { to: '/terms', label: 'Terms' },
          { to: 'https://safmc.net', label: 'SAFMC ↗', external: true }
        ]}
        containerClassName="max-w-[1600px] mx-auto py-5 px-4 sm:px-6 lg:px-8"
      />

      {/* AI Assistant - Available on all pages */}
      <AIAssistant />
    </div>
  );
};

export default Layout;
