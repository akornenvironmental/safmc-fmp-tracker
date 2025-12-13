/**
 * Breadcrumb Navigation Component
 * Shows current page path: SAFMC FMP Tracker > Section > Subsection
 */

import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

const Breadcrumb = ({ customItems = null }) => {
  const location = useLocation();

  // Generate breadcrumb items from URL path
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);

    // Start with empty items array (no home breadcrumb)
    const items = [];

    // Map path segments to readable labels
    const segmentMap = {
      'actions': 'Actions',
      'actions-new': 'Actions',
      'meetings': 'Meetings',
      'calendar': 'Calendar',
      'comments': 'Comments',
      'stocks': 'Stock Assessments',
      'species': 'Stock Assessments',
      'assessments': 'Stock Assessments',
      'workplan': 'Work Plan',
      'compare': 'Compare Actions',
      'ssc': 'SSC',
      'members': 'Members',
      'recommendations': 'Recommendations',
      'cmod': 'CMOD',
      'workshops': 'Workshops',
      'topics': 'Topics',
      'admin': 'Admin',
      'users': 'User Management',
      'logs': 'Activity Logs',
      'feedback': 'Feedback'
    };

    // Special handling for SSC subsections
    if (pathSegments[0] === 'ssc') {
      items.push({ label: 'SSC', path: '/ssc' });

      if (pathSegments[1]) {
        const subsection = segmentMap[pathSegments[1]] || pathSegments[1];
        items.push({
          label: subsection,
          path: `/ssc/${pathSegments[1]}`,
          isLast: true
        });
      }
    }
    // Special handling for CMOD subsections
    else if (pathSegments[0] === 'cmod') {
      items.push({ label: 'CMOD', path: '/cmod' });

      if (pathSegments[1]) {
        const subsection = segmentMap[pathSegments[1]] || 'Workshop Details';
        items.push({
          label: subsection,
          path: `/cmod/${pathSegments[1]}${pathSegments[2] ? '/' + pathSegments[2] : ''}`,
          isLast: true
        });
      }
    }
    // Special handling for species profile
    else if (pathSegments[0] === 'species' && pathSegments[1]) {
      items.push({ label: 'Stock Assessments', path: '/stocks' });
      items.push({
        label: decodeURIComponent(pathSegments[1]),
        path: `/species/${pathSegments[1]}`,
        isLast: true
      });
    }
    // Special handling for admin subsections
    else if (pathSegments[0] === 'admin') {
      items.push({ label: 'Admin', path: '/admin/users' });

      if (pathSegments[1]) {
        const subsection = segmentMap[pathSegments[1]] || pathSegments[1];
        items.push({
          label: subsection,
          path: `/admin/${pathSegments[1]}`,
          isLast: true
        });
      }
    }
    // Standard single-level pages
    else if (pathSegments.length > 0) {
      const segment = pathSegments[0];
      const label = segmentMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
      items.push({
        label,
        path: `/${segment}`,
        isLast: true
      });
    }

    return items;
  };

  const breadcrumbItems = customItems || generateBreadcrumbs();

  // Don't show breadcrumbs on home page
  if (location.pathname === '/' && !customItems) {
    return null;
  }

  return (
    <nav className="flex items-center space-x-2 text-lg mb-6 px-1" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {breadcrumbItems.map((item, index) => (
          <li key={`${item.path}-${index}`} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="w-5 h-5 mx-2 text-gray-400 dark:text-gray-600" />
            )}

            {item.isLast ? (
              <span className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                {item.icon && <item.icon className="w-5 h-5" />}
                {item.label}
              </span>
            ) : (
              <Link
                to={item.path}
                className="text-gray-600 dark:text-gray-400 hover:text-brand-blue dark:hover:text-brand-blue-light transition-colors flex items-center gap-2"
              >
                {item.icon && <item.icon className="w-5 h-5" />}
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumb;
