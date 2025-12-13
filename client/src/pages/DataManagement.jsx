/**
 * Data Management & Utilities
 * Admin page for managing data scrapers and system utilities
 */

import { useState, useEffect } from 'react';
import { RefreshCw, Database, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import Button from '../components/Button';
import ButtonGroup from '../components/ButtonGroup';
import { API_BASE_URL } from '../config';
import { toast } from 'react-toastify';

const DataManagement = () => {
  const [scrapers, setScrapers] = useState([
    {
      id: 'safmc_actions',
      name: 'SAFMC Amendment Actions',
      description: 'Fishery management plan amendments and regulatory actions from safmc.net',
      endpoint: '/api/scrape/all',
      frequency: 'Daily at 2:00 AM EST',
      lastRun: null,
      status: 'idle',
      running: false
    },
    {
      id: 'ssc_meetings',
      name: 'SSC Meetings & Documents',
      description: 'Scientific and Statistical Committee meetings, agendas, and recommendations',
      endpoint: '/api/ssc/import/meetings',
      frequency: 'Weekly on Sundays at 3:00 AM EST',
      lastRun: null,
      status: 'idle',
      running: false
    },
    {
      id: 'cmod_workshops',
      name: 'CMOD Workshops',
      description: 'Council Member Ongoing Development training workshops and materials',
      endpoint: '/api/cmod/import/workshops',
      frequency: 'Weekly on Sundays at 4:00 AM EST',
      lastRun: null,
      status: 'idle',
      running: false
    },
    {
      id: 'ecosystem_data',
      name: 'Ecosystem Indicators',
      description: 'NOAA IEA ecosystem assessment indicators and SOE report data',
      endpoint: '/api/ecosystem/import',
      frequency: 'Monthly on the 1st at 1:00 AM EST',
      lastRun: null,
      status: 'idle',
      running: false
    }
  ]);

  const [updatingAll, setUpdatingAll] = useState(false);

  useEffect(() => {
    fetchScraperStatus();
  }, []);

  const fetchScraperStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/scraper/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        // Update scraper last run times if API provides them
        if (data.scrapers) {
          setScrapers(prev => prev.map(scraper => {
            const status = data.scrapers[scraper.id];
            return status ? { ...scraper, ...status } : scraper;
          }));
        }
      }
    } catch (error) {
      console.error('Error fetching scraper status:', error);
    }
  };

  const runScraper = async (scraper) => {
    try {
      setScrapers(prev => prev.map(s =>
        s.id === scraper.id ? { ...s, running: true, status: 'running' } : s
      ));

      const token = localStorage.getItem('authToken');
      const body = scraper.id === 'ssc_meetings'
        ? JSON.stringify({ download_documents: true })
        : JSON.stringify({});

      const response = await fetch(`${API_BASE_URL}${scraper.endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setScrapers(prev => prev.map(s =>
          s.id === scraper.id
            ? { ...s, running: false, status: 'success', lastRun: new Date().toISOString() }
            : s
        ));
        toast.success(`${scraper.name} completed successfully`);
      } else {
        throw new Error(data.error || 'Scraper failed');
      }
    } catch (error) {
      console.error(`Error running ${scraper.name}:`, error);
      setScrapers(prev => prev.map(s =>
        s.id === scraper.id ? { ...s, running: false, status: 'error' } : s
      ));
      toast.error(`Failed to run ${scraper.name}: ${error.message}`);
    }
  };

  const runAllScrapers = async () => {
    setUpdatingAll(true);

    for (const scraper of scrapers) {
      await runScraper(scraper);
      // Wait 2 seconds between scrapers to avoid overloading
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    setUpdatingAll(false);
    toast.success('All scrapers completed');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const formatLastRun = (timestamp) => {
    if (!timestamp) return 'Never';

    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div>
      <PageHeader
        icon={Database}
        title="Data Management"
        subtitle="System utilities"
        description="Manage automated data scrapers, monitor system health, and manually trigger data updates from external sources."
      />

      <ButtonGroup>
        <Button
          variant="primary"
          icon={RefreshCw}
          onClick={runAllScrapers}
          disabled={updatingAll || scrapers.some(s => s.running)}
        >
          {updatingAll ? 'Updating All...' : 'Update All Data'}
        </Button>
      </ButtonGroup>

      {/* Info Banner */}
      <div className="mb-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">About Data Scrapers</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              The system automatically runs these scrapers on the schedule shown below. You can also manually trigger any scraper to fetch the latest data immediately. Running all scrapers may take several minutes to complete.
            </p>
          </div>
        </div>
      </div>

      {/* Scrapers List */}
      <div className="space-y-4">
        {scrapers.map((scraper) => (
          <div
            key={scraper.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusIcon(scraper.status)}
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {scraper.name}
                  </h3>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {scraper.description}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Schedule:</span>
                    <span className="ml-2 text-gray-600 dark:text-gray-400">{scraper.frequency}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">Last Run:</span>
                    <span className="ml-2 text-gray-600 dark:text-gray-400">
                      {formatLastRun(scraper.lastRun)}
                    </span>
                  </div>
                </div>
              </div>

              <Button
                variant="secondary"
                icon={RefreshCw}
                onClick={() => runScraper(scraper)}
                disabled={scraper.running || updatingAll}
              >
                {scraper.running ? 'Running...' : 'Run Now'}
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DataManagement;
