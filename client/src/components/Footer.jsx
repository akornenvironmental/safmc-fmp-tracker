import { Link } from 'react-router-dom';
import { useSidebar } from '../contexts/SidebarContext';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  const { isCollapsed } = useSidebar();

  return (
    <footer className={`bg-gradient-to-r from-brand-blue to-brand-blue-dark border-t-4 border-brand-green mt-auto transition-all duration-300 ${
      isCollapsed ? 'ml-14' : 'ml-48'
    }`}>
      <div className="py-5 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-3">
          {/* Top Row: Title and Version */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 pb-2 border-b border-blue-300/30">
            <h3 className="text-lg font-bold text-white">SAFMC FMP Tracker</h3>

            {/* Version and Secure Badge */}
            <div className="flex items-center gap-3 text-base text-blue-100">
              <span>v1.0.0</span>
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4 text-brand-green" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Desktop Optimized
              </span>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="pb-2 border-b border-blue-300/30">
            <p className="text-base text-blue-100 leading-relaxed">
              <strong className="text-white">Public Data System.</strong> This system contains publicly available data from SAFMC.net, including fishery management plan amendments, council meetings, public comments, and stock assessments. All data is sourced from official SAFMC publications.
            </p>
            <p className="text-xs text-blue-200 mt-2">
              This system uses AI-powered tools to assist with data analysis and organization. All AI-generated suggestions should be reviewed for accuracy.
            </p>
          </div>

          {/* Bottom Row: Logo, Copyright, Contact & Links */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-base">
              <p className="text-white">
                © {currentYear} <a href="https://akornenvironmental.com/" target="_blank" rel="noopener noreferrer" className="font-medium hover:text-brand-green transition-colors">akorn environmental consulting, LLC</a>
              </p>
              <span className="hidden sm:inline text-blue-300">•</span>
              <p className="text-blue-100">
                Issues? Suggestions? <a href="mailto:aaron.kornbluth@gmail.com?subject=SAFMC%20FMP%20Tracker%20Feedback" className="hover:text-brand-green transition-colors underline">Contact Aaron</a>
              </p>
            </div>

            {/* Links */}
            <div className="flex gap-4 text-base">
              <Link to="/privacy" className="text-blue-100 hover:text-brand-green transition-colors whitespace-nowrap">Privacy</Link>
              <Link to="/terms" className="text-blue-100 hover:text-brand-green transition-colors whitespace-nowrap">Terms</Link>
              <a href="https://safmc.net" target="_blank" rel="noopener noreferrer" className="text-blue-100 hover:text-brand-green transition-colors whitespace-nowrap">SAFMC ↗</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
