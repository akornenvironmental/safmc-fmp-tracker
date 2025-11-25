import { Link } from 'react-router-dom';
import { Shield, CheckCircle } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="footer" className="bg-gradient-to-r from-brand-blue to-blue-700 text-white mt-auto border-t-4 border-brand-green">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column - Notices */}
          <div className="space-y-4">
            {/* Privacy Notice */}
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-brand-green flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm mb-1">Public Data System</h3>
                <p className="text-xs text-blue-100 leading-relaxed">
                  This system contains publicly available data from SAFMC.net, including fishery management plan amendments,
                  council meetings, public comments, and stock assessments. All data is sourced from official SAFMC publications.
                </p>
              </div>
            </div>

            {/* AI Notice */}
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-brand-green flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm mb-1">AI-Powered Analysis</h3>
                <p className="text-xs text-blue-100 leading-relaxed">
                  This system uses AI-powered tools to assist with data analysis and organization.
                  All AI-generated information should be independently verified for accuracy.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column - System Info */}
          <div className="space-y-4">
            {/* System Info */}
            <div>
              <h3 className="font-semibold text-lg mb-2">SAFMC FMP Tracker</h3>
              <p className="text-sm text-blue-100 mb-3">
                Fishery Management Plan Amendment Tracking System
              </p>
              <div className="flex items-center gap-3 text-xs text-blue-200">
                <span className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  v1.0.0
                </span>
                <span>•</span>
                <span>Desktop Optimized</span>
              </div>
            </div>

            {/* Links */}
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs">
              <Link to="/privacy" className="text-blue-200 hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link to="/terms" className="text-blue-200 hover:text-white transition-colors">
                Terms of Service
              </Link>
              <a
                href="https://safmc.net"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-200 hover:text-white transition-colors"
              >
                SAFMC.net
              </a>
            </div>

            {/* Copyright */}
            <div className="pt-4 border-t border-blue-400/30">
              <p className="text-xs text-blue-200">
                © {currentYear}{' '}
                <a
                  href="https://akornenvironmental.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white hover:text-brand-green font-medium transition-colors"
                >
                  akorn environmental consulting, LLC
                </a>
              </p>
              <p className="text-xs text-blue-200 mt-2">
                Questions? Issues? Contact{' '}
                <a
                  href="mailto:aaron.kornbluth@gmail.com?subject=SAFMC%20FMP%20Tracker%20Feedback"
                  className="text-white hover:text-brand-green transition-colors underline"
                >
                  Aaron Kornbluth
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
