/**
 * Standardized Button Component
 *
 * Provides consistent button styling across the application with variants:
 * - primary: Solid brand-blue background (main actions)
 * - secondary: Outline with brand-blue border (secondary actions)
 * - danger: Red background or outline (destructive actions)
 * - ghost: Transparent background (tertiary actions)
 */

const Button = ({
  children,
  variant = 'primary',
  onClick,
  disabled = false,
  icon: Icon,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-brand-blue text-white hover:bg-brand-blue-light focus:ring-brand-blue',
    secondary: 'border border-brand-blue text-brand-blue bg-white dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-gray-700 focus:ring-brand-blue',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    'danger-outline': 'border border-red-600 text-red-600 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20 focus:ring-red-500',
    ghost: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-gray-500',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
};

export default Button;
