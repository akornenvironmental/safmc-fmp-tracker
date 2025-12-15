/**
 * Standardized PageControlsContainer Component
 * Provides consistent layout container for search, filters, and actions
 */

const PageControlsContainer = ({ children, className = "" }) => {
  return (
    <div className={`flex flex-wrap items-stretch gap-2 mb-6 ${className}`}>
      {children}
    </div>
  );
};

export default PageControlsContainer;
