/**
 * Button Group Component
 *
 * Groups related buttons together with consistent spacing.
 * Positioned below the PageHeader component.
 */

const ButtonGroup = ({ children, className = '' }) => {
  return (
    <div className={`flex items-center gap-2 mb-6 ${className}`}>
      {children}
    </div>
  );
};

export default ButtonGroup;
