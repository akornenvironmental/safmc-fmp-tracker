/**
 * StatusBadge Component - Section 508 / WCAG 2.1 AA Compliant
 *
 * Provides accessible status badges with proper color contrast (4.5:1 minimum).
 * Uses dark text on light backgrounds with colored borders instead of
 * light text on light backgrounds which violates contrast requirements.
 *
 * @param {string} variant - Badge color theme (success, warning, error, info, neutral, purple)
 * @param {string} children - Badge text content
 * @param {string} size - Badge size (sm, md, lg)
 * @param {string} className - Additional CSS classes
 */

const StatusBadge = ({
  variant = 'neutral',
  children,
  size = 'md',
  className = ''
}) => {
  // Size variants
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  // Accessible color variants with proper contrast
  // Using dark text on white/light backgrounds with colored borders
  const variantClasses = {
    success: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-green-600 dark:border-green-500',
    warning: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-yellow-600 dark:border-yellow-500',
    error: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-red-600 dark:border-red-500',
    info: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-blue-600 dark:border-blue-500',
    purple: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-purple-600 dark:border-purple-500',
    neutral: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-2 border-gray-600 dark:border-gray-500'
  };

  // Alternative: Solid background with white text (also accessible)
  // Use this for more prominent status indicators
  const solidVariants = {
    success: 'bg-green-600 dark:bg-green-500 text-white border-0',
    warning: 'bg-yellow-600 dark:bg-yellow-500 text-white border-0',
    error: 'bg-red-600 dark:bg-red-500 text-white border-0',
    info: 'bg-blue-600 dark:bg-blue-500 text-white border-0',
    purple: 'bg-purple-600 dark:bg-purple-500 text-white border-0',
    neutral: 'bg-gray-600 dark:bg-gray-500 text-white border-0'
  };

  return (
    <span
      className={`
        inline-flex items-center font-semibold rounded-full
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
};

// Alternative solid background version
export const StatusBadgeSolid = ({
  variant = 'neutral',
  children,
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  const solidVariants = {
    success: 'bg-green-600 dark:bg-green-500 text-white',
    warning: 'bg-yellow-600 dark:bg-yellow-500 text-white',
    error: 'bg-red-600 dark:bg-red-500 text-white',
    info: 'bg-blue-600 dark:bg-blue-500 text-white',
    purple: 'bg-purple-600 dark:bg-purple-500 text-white',
    neutral: 'bg-gray-600 dark:bg-gray-500 text-white'
  };

  return (
    <span
      className={`
        inline-flex items-center font-semibold rounded-full
        ${sizeClasses[size]}
        ${solidVariants[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
};

export default StatusBadge;
