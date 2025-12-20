/**
 * Ecosystem Assessment Page
 *
 * Displays ecosystem indicators and assessments from NOAA IEA South Atlantic
 * Links to external resources and displays available ecosystem data
 */

import { Link } from 'react-router-dom';
import {
  TrendingUp, ExternalLink, Database, FileText, Activity,
  Waves, Thermometer, Fish, Users, AlertCircle, Download, BarChart3
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

const Ecosystem = () => {

  // Ecosystem indicator categories based on Northeast IEA model
  const indicatorCategories = [
    {
      title: 'Climate & Physical',
      icon: Thermometer,
      color: 'blue',
      description: 'Sea surface temperature, ocean currents, climate patterns',
      indicators: [
        { name: 'Sea Surface Temperature', status: 'external', source: 'NOAA' },
        { name: 'Gulf Stream Position', status: 'external', source: 'NOAA' },
        { name: 'Ocean Heat Content', status: 'external', source: 'NOAA' },
        { name: 'Salinity', status: 'external', source: 'NOAA' },
      ]
    },
    {
      title: 'Biological',
      icon: Fish,
      color: 'green',
      description: 'Fish populations, habitat quality, species diversity',
      indicators: [
        { name: 'Stock Assessments', status: 'integrated', source: 'SAFMC', link: '/stocks' },
        { name: 'Coral Health', status: 'external', source: 'NOAA' },
        { name: 'Protected Species', status: 'external', source: 'NOAA' },
        { name: 'Habitat Mapping', status: 'external', source: 'NOAA' },
      ]
    },
    {
      title: 'Fisheries',
      icon: Activity,
      color: 'purple',
      description: 'Commercial and recreational fishing metrics',
      indicators: [
        { name: 'Commercial Landings', status: 'external', source: 'NOAA Fisheries' },
        { name: 'Recreational Landings', status: 'external', source: 'MRIP' },
        { name: 'Fishing Effort', status: 'external', source: 'NOAA' },
        { name: 'Fleet Capacity', status: 'external', source: 'NOAA' },
      ]
    },
    {
      title: 'Human Dimensions',
      icon: Users,
      color: 'orange',
      description: 'Economic and social indicators',
      indicators: [
        { name: 'Economic Value', status: 'external', source: 'NOAA Fisheries' },
        { name: 'Jobs & Communities', status: 'external', source: 'NOAA' },
        { name: 'Recreational Participation', status: 'external', source: 'MRIP' },
        { name: 'Public Comments', status: 'integrated', source: 'SAFMC', link: '/comments' },
      ]
    }
  ];

  // External resources
  const externalResources = [
    {
      title: 'South Atlantic Ecosystem Status Report',
      url: 'https://www.integratedecosystemassessment.noaa.gov/regions/gulf-mexico/south-atlantic-ecosystem-status-report',
      description: 'Comprehensive ecosystem assessment from NOAA IEA',
      icon: FileText,
      color: 'blue'
    },
    {
      title: 'Northeast IEA ecodata Package',
      url: 'https://github.com/NOAA-EDAB/ecodata',
      description: 'Model for automated ecosystem indicator data (100+ indicators)',
      icon: Database,
      color: 'green'
    },
    {
      title: 'NOAA Fisheries Economics',
      url: 'https://www.fisheries.noaa.gov/national/sustainable-fisheries/fisheries-economics-united-states',
      description: 'Economic data and analysis for U.S. fisheries',
      icon: BarChart3,
      color: 'purple'
    },
    {
      title: 'SAFMC Habitat Protection',
      url: 'https://safmc.net/managed-areas/habitat-protection/',
      description: 'Habitat areas of particular concern and ecosystem protections',
      icon: Waves,
      color: 'teal'
    }
  ];

  const getStatusBadge = (status) => {
    if (status === 'integrated') {
      return (
        <StatusBadge variant="success" size="sm">
          <Activity className="w-3 h-3" />
          Integrated
        </StatusBadge>
      );
    }
    return (
      <StatusBadge variant="neutral" size="sm">
        <ExternalLink className="w-3 h-3" />
        External
      </StatusBadge>
    );
  };

  const getCategoryColor = (color) => {
    const colors = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-green-500 to-green-600',
      purple: 'from-purple-500 to-purple-600',
      orange: 'from-orange-500 to-orange-600',
      teal: 'from-teal-500 to-teal-600',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div>
      {/* Description */}
      <div className="page-description-container">
        <p className="page-description-text">
          NOAA Integrated Ecosystem Assessment indicators and State of the Ecosystem reports for fishery management.
        </p>
        <div className="page-description-actions"></div>
      </div>

      {/* Ecosystem Indicator Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {indicatorCategories.map((category) => {
          const Icon = category.icon;
          return (
            <div
              key={category.title}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              {/* Category Header */}
              <div className={`bg-gradient-to-r ${getCategoryColor(category.color)} p-4`}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">{category.title}</h2>
                    <p className="text-sm text-white/90">{category.description}</p>
                  </div>
                </div>
              </div>

              {/* Indicators List */}
              <div className="p-4">
                <div className="space-y-2">
                  {category.indicators.map((indicator, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {indicator.status === 'integrated' && indicator.link ? (
                            <Link
                              to={indicator.link}
                              className="text-sm font-medium text-brand-blue dark:text-brand-blue-light hover:underline"
                            >
                              {indicator.name}
                            </Link>
                          ) : (
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                              {indicator.name}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          Source: {indicator.source}
                        </p>
                      </div>
                      {getStatusBadge(indicator.status)}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* External Resources */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Database className="w-5 h-5 text-brand-blue dark:text-brand-blue-light" />
          External Data Resources
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {externalResources.map((resource, idx) => {
            const Icon = resource.icon;
            return (
              <a
                key={idx}
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-start gap-4 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-brand-blue dark:hover:border-brand-blue-light hover:shadow-md transition-all"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getCategoryColor(resource.color)} flex items-center justify-center flex-shrink-0`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-brand-blue dark:group-hover:text-brand-blue-light transition-colors">
                      {resource.title}
                    </h3>
                    <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-brand-blue dark:group-hover:text-brand-blue-light transition-colors" />
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {resource.description}
                  </p>
                </div>
              </a>
            );
          })}
        </div>
      </div>

      {/* Future Development Notice */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6">
        <div className="flex items-start gap-4">
          <TrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Future Data Integration
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
              We're working to integrate automated ecosystem indicator data similar to the Northeast IEA's ecodata package.
              This will provide:
            </p>
            <ul className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400"></div>
                Real-time ecosystem indicator dashboards
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400"></div>
                Automated data updates from NOAA sources
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400"></div>
                Historical trend analysis and visualizations
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400"></div>
                Integration with FMP decisions and stock assessments
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Ecosystem;
