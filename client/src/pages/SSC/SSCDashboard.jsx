/**
 * SSC Dashboard
 * Overview of SSC activities, upcoming meetings, and recent recommendations
 */

import { useState } from 'react';
import { FlaskConical, Users, Calendar, FileText, TrendingUp, Download, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button';
import { API_BASE_URL } from '../../config';
import { toast } from 'react-toastify';

const SSCDashboard = () => {
  const [importing, setImporting] = useState(false);

  const handleImportMeetings = async () => {
    if (!confirm('Import all SSC meetings from safmc.net? This may take several minutes and will download meeting documents.')) {
      return;
    }

    setImporting(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/ssc/import/meetings`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ download_documents: true })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to import SSC meetings');
      }

      toast.success(`Import complete! ${data.stats.meetings_created} meetings created, ${data.stats.documents_created} documents imported`);
    } catch (err) {
      console.error('Error importing SSC meetings:', err);
      toast.error(err.message || 'Failed to import SSC meetings');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div>
      {/* Description */}
      <div className="page-description-container">
        <p className="page-description-text">
          The SSC provides independent scientific advice on fishery management decisions and stock assessments.
        </p>
        <div className="page-description-actions"></div>
      </div>

      {/* Admin Actions */}
      <div className="mb-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Download className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Import SSC Meetings</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Import all SSC meetings from safmc.net with documents and recommendations
              </p>
            </div>
          </div>
          <Button
            variant="primary"
            icon={Download}
            onClick={handleImportMeetings}
            disabled={importing}
          >
            {importing ? 'Importing...' : 'Import Meetings'}
          </Button>
        </div>
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

        <Link
          to="/ssc/meetings"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700 group"
        >
          <Calendar className="w-10 h-10 text-brand-blue mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Meetings</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            View SSC meeting schedule
          </p>
        </Link>

        <Link
          to="/ssc/recommendations"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700 group"
        >
          <FileText className="w-10 h-10 text-brand-blue mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Recommendations</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Track SSC recommendations
          </p>
        </Link>

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
