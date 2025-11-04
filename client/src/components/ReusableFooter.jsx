/**
 * ReusableFooter Component
 *
 * A fully customizable footer component with multiple sections:
 * - App title and version
 * - Feature badges (AI-powered, etc.)
 * - Description/privacy notice
 * - Copyright and contact info
 * - Footer links
 */

import { Link } from 'react-router-dom';

export default function ReusableFooter({
  // Branding
  appName,
  version,
  companyName,
  companyUrl,

  // Content
  description,
  aiNotice,
  contactEmail,
  contactSubject,

  // Links
  footerLinks = [],

  // Feature badges
  featureBadges = [],
  showAIPoweredBadge = false,

  // Styling
  footerClassName = 'bg-gradient-to-r from-brand-blue to-brand-blue-dark border-t-4 border-brand-green mt-auto',
  containerClassName = 'max-w-7xl mx-auto py-5 px-4 sm:px-6 lg:px-8',
  appTitleClassName = 'text-lg font-bold text-white',
  versionClassName = 'text-base text-blue-100',
  descriptionClassName = 'text-base text-blue-100 leading-relaxed',
  copyrightClassName = 'text-white',
  linkClassName = 'text-blue-100 hover:text-brand-green transition-colors',

  // Feature toggles
  showVersion = true,
  showDescription = true,
  showAINotice = true,
  showCopyright = true,
  showContact = true,
  showFooterLinks = true,
  showTopBorder = true,

  // Custom content
  customContent,
}) {
  const currentYear = new Date().getFullYear();

  // Default AI badge
  const defaultAIBadge = {
    icon: (
      <svg className="w-4 h-4 text-brand-green" fill="currentColor" viewBox="0 0 20 20">
        <path d="M13 7H7v6h6V7z" />
        <path
          fillRule="evenodd"
          d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z"
          clipRule="evenodd"
        />
      </svg>
    ),
    label: 'AI-Powered',
  };

  const allBadges = showAIPoweredBadge ? [defaultAIBadge, ...featureBadges] : featureBadges;

  return (
    <footer className={footerClassName}>
      <div className={containerClassName}>
        <div className="flex flex-col gap-3">
          {/* Top Row: Title, Version, and Badges */}
          <div className={`flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 ${showTopBorder ? 'pb-2 border-b border-blue-300/30' : ''}`}>
            <h3 className={appTitleClassName}>{appName}</h3>

            {/* Version and Badges */}
            {(showVersion || allBadges.length > 0) && (
              <div className="flex items-center gap-3 text-base text-blue-100">
                {showVersion && version && <span className={versionClassName}>v{version}</span>}
                {allBadges.map((badge, index) => (
                  <span key={index} className={badge.className || 'flex items-center gap-1'}>
                    {badge.icon}
                    {badge.label}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Description and AI Notice */}
          {(showDescription || showAINotice) && (
            <div className="pb-2 border-b border-blue-300/30">
              {showDescription && description && (
                <div className={descriptionClassName}>
                  {typeof description === 'string' ? <p>{description}</p> : description}
                </div>
              )}
              {showAINotice && aiNotice && (
                <p className="text-xs text-blue-200 mt-2">
                  {aiNotice}
                </p>
              )}
            </div>
          )}

          {/* Custom Content Area */}
          {customContent && <div className="pb-2 border-b border-blue-300/30">{customContent}</div>}

          {/* Bottom Row: Copyright, Contact & Links */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-base">
              {/* Copyright */}
              {showCopyright && (
                <p className={copyrightClassName}>
                  © {currentYear}{' '}
                  {companyUrl ? (
                    <a
                      href={companyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium hover:text-brand-green transition-colors"
                    >
                      {companyName || appName}
                    </a>
                  ) : (
                    companyName || appName
                  )}
                </p>
              )}

              {/* Contact */}
              {showContact && contactEmail && (
                <>
                  <span className="hidden sm:inline text-blue-300">•</span>
                  <p className="text-blue-100">
                    Issues? Suggestions?{' '}
                    <a
                      href={`mailto:${contactEmail}${contactSubject ? `?subject=${encodeURIComponent(contactSubject)}` : ''}`}
                      className="hover:text-brand-green transition-colors underline"
                    >
                      Contact Us
                    </a>
                  </p>
                </>
              )}
            </div>

            {/* Footer Links */}
            {showFooterLinks && footerLinks.length > 0 && (
              <div className="flex gap-4 text-base">
                {footerLinks.map((link, index) => {
                  if (link.external) {
                    return (
                      <a
                        key={index}
                        href={link.to}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`${linkClassName} whitespace-nowrap`}
                      >
                        {link.label}
                      </a>
                    );
                  }

                  return (
                    <Link
                      key={index}
                      to={link.to}
                      className={`${linkClassName} whitespace-nowrap`}
                    >
                      {link.label}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </footer>
  );
}
