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
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navLinks = [
    { to: '/', label: 'Dashboard' },
    { to: '/actions', label: 'Actions' },
    { to: '/meetings', label: 'Meetings' },
    { to: '/comments', label: 'Comments' }
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
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <ReusableHeader
        appName="SAFMC FMP Tracker"
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
        onLogoutClick={handleLogout}
        containerClassName="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8"
      />

      <main className="max-w-[1600px] mx-auto py-6 sm:px-6 lg:px-8 flex-grow w-full">
        <Outlet />
      </main>

      <ReusableFooter
        appName="SAFMC FMP Tracker"
        version="1.0.0"
        companyName="akorn environmental consulting, LLC"
        companyUrl="https://akornenvironmental.com/"
        description={customDescription}
        aiNotice="This system uses AI-powered analysis to assist with tracking and summarization. All information should be verified against official SAFMC sources."
        contactEmail="aaron.kornbluth@gmail.com"
        contactSubject="SAFMC FMP Tracker Feedback"
        featureBadges={featureBadges}
        showAIPoweredBadge={false}
        customContent={customFooterContent}
        containerClassName="max-w-[1600px] mx-auto py-5 px-4 sm:px-6 lg:px-8"
      />

      {/* AI Assistant - Available on all pages */}
      <AIAssistant />
    </div>
  );
};

export default Layout;
