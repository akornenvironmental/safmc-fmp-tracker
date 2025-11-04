import { Link } from 'react-router-dom';
import safmcLogo from '../assets/safmc-logo.jpg';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gradient-to-r from-brand-blue to-brand-blue-dark border-t-4 border-brand-green mt-auto">
      <div className="max-w-[1600px] mx-auto py-5 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-3">
          {/* Top Row: Logo, Title and Version */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 pb-2 border-b border-blue-300/30">
            <div className="flex items-center gap-3">
              <img src={safmcLogo} alt="SAFMC Logo" className="h-12 w-auto rounded" />
              <h3 className="text-lg font-bold text-white">SAFMC FMP Tracker</h3>
            </div>

            {/* Version and Public Data Badge */}
            <div className="flex items-center gap-3 text-base text-blue-100">
              <span>v1.0.0</span>
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4 text-brand-green" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Public Data
              </span>
            </div>
          </div>

          {/* Data Source Notice */}
          <div className="pb-2 border-b border-blue-300/30">
            <p className="text-base text-blue-100 leading-relaxed">
              <strong className="text-white">Fishery Management Plan Tracking System.</strong> This system tracks amendments, meetings, and public comments for South Atlantic FMPs. All data is sourced from publicly available information on SAFMC.net.
            </p>
            <p className="text-xs text-blue-200 mt-2">
              This system uses AI-powered analysis to assist with tracking and summarization. All information should be verified against official SAFMC sources.
            </p>
          </div>

          {/* Bottom Row: Copyright, Contact & Links */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-base">
              <p className="text-white">
                © {currentYear} <a href="https://akornenvironmental.com/" target="_blank" rel="noopener noreferrer" className="font-medium hover:text-brand-green transition-colors">akorn environmental consulting, LLC</a>
              </p>
              <span className="hidden sm:inline text-blue-300">•</span>
              <p className="text-blue-200 italic">Desktop optimized</p>
              <span className="hidden sm:inline text-blue-300">•</span>
              <p className="text-blue-100">
                Issues? Suggestions? <a href="mailto:aaron.kornbluth@gmail.com?subject=SAFMC%20FMP%20Tracker%20Feedback" className="hover:text-brand-green transition-colors underline">Contact Aaron</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
