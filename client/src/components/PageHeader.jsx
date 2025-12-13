/**
 * Standardized Page Header Component
 *
 * Ensures consistent formatting across all pages with:
 * - Icon + Title (h1)
 * - Subtitle (small gray text)
 * - Description paragraph (medium text) positioned top-right
 */

const PageHeader = ({ icon: Icon, title, subtitle, description }) => {
  return (
    <div className="mb-6 flex items-start justify-between gap-6">
      {/* Left: Icon + Title + Subtitle */}
      <div className="flex items-center gap-3">
        <Icon className="w-8 h-8 text-brand-blue flex-shrink-0" />
        <div>
          <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-white">
            {title}
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {subtitle}
          </p>
        </div>
      </div>

      {/* Right: Description */}
      <p className="text-base text-gray-700 dark:text-gray-300 max-w-md text-right flex-shrink-0">
        {description}
      </p>
    </div>
  );
};

export default PageHeader;
