/**
 * SSC Dashboard
 * Overview of SSC activities, upcoming meetings, and recent recommendations
 */

import { FlaskConical, Users, Calendar, FileText, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const SSCDashboard = () => {
  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <FlaskConical className="w-8 h-8 text-brand-blue" />
          <div>
            <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-white">
              Scientific & Statistical Committee
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              SSC Dashboard & Overview
            </p>
          </div>
        </div>
        <p className="text-gray-700 dark:text-gray-300 max-w-3xl">
          The SSC provides independent scientific advice to the South Atlantic Fishery Management Council
          on stock assessments, acceptable biological catch (ABC) recommendations, and fishery management measures.
        </p>
      </div>

      {/* Quick Links Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Link
          to="/ssc/members"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700 group"
        >
          <Users className="w-10 h-10 text-brand-blue mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Members</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            View all 21 SSC members
          </p>
        </Link>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700 opacity-50">
          <Calendar className="w-10 h-10 text-gray-400 mb-3" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Meetings</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Coming soon
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700 opacity-50">
          <FileText className="w-10 h-10 text-gray-400 mb-3" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Recommendations</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Coming soon
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700 opacity-50">
          <TrendingUp className="w-10 h-10 text-gray-400 mb-3" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Analytics</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Coming soon
          </p>
        </div>
      </div>

      {/* Info Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* About SSC */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            About the SSC
          </h2>
          <div className="space-y-3 text-gray-700 dark:text-gray-300 text-sm">
            <p>
              The Scientific and Statistical Committee (SSC) is responsible for reviewing
              the scientific basis of Council management plans and actions to develop
              fishing level recommendations.
            </p>
            <p>
              The SSC comprises 21 members representing:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Biologists and stock assessment scientists</li>
              <li>Economists and social scientists</li>
              <li>Natural resource specialists</li>
            </ul>
            <p>
              The Committee meets at least twice annually to address stock assessments,
              management evaluations, social and economic analyses, habitat evaluations,
              and ecosystem management issues.
            </p>
          </div>
        </div>

        {/* SSC Leadership */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            SSC Leadership
          </h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center text-white font-bold flex-shrink-0">
                MR
              </div>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  Dr. Marcel Reichert
                </div>
                <div className="text-sm text-yellow-700 dark:text-yellow-300 font-medium">
                  Chair
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  South Carolina • At-large
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold flex-shrink-0">
                WB
              </div>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  Dr. Walter Bubley
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-300 font-medium">
                  Vice-Chair
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  South Carolina • State-designated
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SSCDashboard;
