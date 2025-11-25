import { Link } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="footer" className="bg-[#0A1F3D] text-white mt-auto border-t-2 border-brand-green">
      <div className="max-w-4xl mx-auto px-8 py-12 text-center">
        {/* Header with Title and Version */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">SAFMC FMP Tracker</h2>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1 text-sm text-gray-300">
              <CheckCircle className="w-4 h-4" />
              v1.0.0
            </span>
            <span className="text-sm text-gray-300">•</span>
            <span className="flex items-center gap-1.5 text-sm">
              <CheckCircle className="w-4 h-4 text-brand-green" />
              <span className="text-white font-medium">Desktop Optimized</span>
            </span>
          </div>
        </div>

        {/* Subtitle */}
        <p className="text-base text-gray-300 mb-8">
          Fishery Management Plan Amendment Tracking System
        </p>

        {/* Public Data Notice */}
        <div className="mb-6">
          <p className="text-sm text-gray-300 leading-relaxed">
            <span className="font-semibold text-white">Public Data System.</span> This system contains publicly available data from SAFMC.net, including fishery management plan amendments, council meetings, public comments, and stock assessments. All data is sourced from official SAFMC publications.
          </p>
        </div>

        {/* AI Notice */}
        <div className="mb-8">
          <p className="text-sm text-gray-400 leading-relaxed">
            This system uses AI-powered tools to assist with data analysis and organization. All AI-generated suggestions should be reviewed for accuracy.
          </p>
        </div>

        {/* Links */}
        <div className="flex justify-center gap-6 text-sm mb-6">
          <Link to="/privacy" className="text-gray-300 hover:text-white transition-colors">
            Privacy Policy
          </Link>
          <Link to="/terms" className="text-gray-300 hover:text-white transition-colors">
            Terms of Service
          </Link>
          <a
            href="https://safmc.net"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-300 hover:text-white transition-colors"
          >
            SAFMC.net
          </a>
        </div>

        {/* Copyright */}
        <div className="text-sm text-gray-400">
          <p>
            © {currentYear}{' '}
            <a
              href="https://akornenvironmental.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white hover:text-brand-green font-medium transition-colors"
            >
              akorn environmental consulting, LLC
            </a>
            {' '}• Issues? Suggestions?{' '}
            <a
              href="mailto:aaron.kornbluth@gmail.com?subject=SAFMC%20FMP%20Tracker%20Feedback"
              className="text-white hover:text-brand-green transition-colors underline"
            >
              Contact Aaron
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
