import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import Button from '../components/Button';
import StatusBadge from '../components/StatusBadge';
import {
  DollarSign,
  Users,
  BarChart3,
  FileText,
  Database,
  TrendingUp,
  Download,
  Plus,
  CheckCircle2,
  Clock,
  AlertCircle,
  ExternalLink,
  RefreshCw
} from 'lucide-react';

const ResourceAllocation = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [isDatabaseInitialized, setIsDatabaseInitialized] = useState(false);

  // Dashboard data
  const [dashboardSummary, setDashboardSummary] = useState(null);

  // Councils & entities
  const [councils, setCouncils] = useState([]);
  const [selectedCouncil, setSelectedCouncil] = useState('ALL');

  // Budget data
  const [budgetComparison, setBudgetComparison] = useState([]);
  const [selectedFiscalYear, setSelectedFiscalYear] = useState(2024);

  // Efficiency metrics
  const [efficiencyMetrics, setEfficiencyMetrics] = useState([]);

  // Data sources
  const [dataSources, setDataSources] = useState([]);

  // Documents
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedFiscalYear) {
      fetchBudgetComparison();
      fetchEfficiencyMetrics();
    }
  }, [selectedFiscalYear]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchDashboardSummary(),
        fetchCouncils(),
        fetchDataSources(),
        fetchDocuments()
      ]);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching initial data:', error);
      setLoading(false);
    }
  };

  const fetchDashboardSummary = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resource-allocation/dashboard`);
      const data = await response.json();
      if (data.success) {
        setDashboardSummary(data.summary);
        if (data.summary.latestFiscalYear) {
          setSelectedFiscalYear(data.summary.latestFiscalYear);
        }
      }
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
    }
  };

  const fetchCouncils = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resource-allocation/councils`);
      const data = await response.json();
      if (data.success && data.councils && data.councils.length > 0) {
        setCouncils(data.councils);
        setIsDatabaseInitialized(true);
      } else {
        setIsDatabaseInitialized(false);
      }
    } catch (error) {
      console.error('Error fetching councils:', error);
      setIsDatabaseInitialized(false);
    }
  };

  const fetchBudgetComparison = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/resource-allocation/analysis/budget-comparison?fiscalYear=${selectedFiscalYear}`
      );
      const data = await response.json();
      if (data.success) {
        setBudgetComparison(data.comparison);
      }
    } catch (error) {
      console.error('Error fetching budget comparison:', error);
    }
  };

  const fetchEfficiencyMetrics = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/resource-allocation/analysis/efficiency-metrics?fiscalYear=${selectedFiscalYear}`
      );
      const data = await response.json();
      if (data.success) {
        setEfficiencyMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Error fetching efficiency metrics:', error);
    }
  };

  const fetchDataSources = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resource-allocation/data-sources`);
      const data = await response.json();
      if (data.success) {
        setDataSources(data.sources);
      }
    } catch (error) {
      console.error('Error fetching data sources:', error);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resource-allocation/documents`);
      const data = await response.json();
      if (data.success) {
        setDocuments(data.documents);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const runMigration = async () => {
    if (!confirm('This will create the resource allocation database tables. Continue?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/resource-allocation/migrate`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        alert(`Migration successful! Created ${data.total_tables} tables.`);
        setIsDatabaseInitialized(true);
        fetchInitialData();
      } else {
        alert(`Migration failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Migration error:', error);
      alert('Migration failed. Check console for details.');
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num, decimals = 1) => {
    if (num === null || num === undefined) return 'N/A';
    return Number(num).toFixed(decimals);
  };

  // Tab content renderers
  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Councils Tracked</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                {dashboardSummary?.councilsCount || 0}
              </p>
            </div>
            <BarChart3 className="h-12 w-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Data Collection</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                {dashboardSummary?.dataCollectionProgress || 0}%
              </p>
            </div>
            <Database className="h-12 w-12 text-green-500" />
          </div>
          <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{ width: `${dashboardSummary?.dataCollectionProgress || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Data Sources</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                {dashboardSummary?.dataSourcesCompleted || 0}/{dashboardSummary?.dataSourcesTotal || 0}
              </p>
            </div>
            <CheckCircle2 className="h-12 w-12 text-emerald-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Documents</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                {dashboardSummary?.documentsCount || 0}
              </p>
            </div>
            <FileText className="h-12 w-12 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Project Description */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Analysis Overview
        </h3>
        <div className="prose dark:prose-invert max-w-none text-sm">
          <p className="text-gray-700 dark:text-gray-300">
            This resource allocation analysis examines budget and staffing disparities across all eight
            regional fishery management councils to test whether SAFMC, SERO, and SEFSC are disadvantaged
            by serving three councils across a vast geographic area.
          </p>
          <p className="text-gray-700 dark:text-gray-300 mt-3">
            <strong>Key Question:</strong> Are SAFMC, SERO, and SEFSC receiving proportional resources compared
            to other regions given their workload, geographic scope, and management complexity?
          </p>
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button
            variant="outline"
            onClick={() => setActiveTab('budget')}
            icon={DollarSign}
          >
            View Budget Analysis
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('staffing')}
            icon={Users}
          >
            View Staffing Metrics
          </Button>
          <Button
            variant="outline"
            onClick={() => setActiveTab('data-collection')}
            icon={Database}
          >
            Data Collection Progress
          </Button>
        </div>
      </div>
    </div>
  );

  const renderBudgetTab = () => (
    <div className="space-y-6">
      {/* Controls */}
      <PageControlsContainer>
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Fiscal Year:
          </label>
          <select
            value={selectedFiscalYear}
            onChange={(e) => setSelectedFiscalYear(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            {[2024, 2023, 2022, 2021, 2020].map(year => (
              <option key={year} value={year}>FY {year}</option>
            ))}
          </select>
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={fetchBudgetComparison}>
            Refresh
          </Button>
        </div>
      </PageControlsContainer>

      {/* Budget Comparison Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Budget Comparison - FY {selectedFiscalYear}
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Council
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Operating Budget
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total Budget
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Inflation Adjusted
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {budgetComparison.length > 0 ? (
                budgetComparison.map((item, idx) => (
                  <tr
                    key={idx}
                    className={`hover:bg-gray-50 dark:hover:bg-gray-900 ${
                      item.councilCode === 'SAFMC' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {item.councilCode}
                        </div>
                        <div className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                          {item.councilName}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                      {formatCurrency(item.operatingBudget)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white font-medium">
                      {formatCurrency(item.totalBudget)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                      {formatCurrency(item.inflationAdjustedTotal)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                    No budget data available for FY {selectedFiscalYear}. Add data to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Budget Data Button */}
      <div className="flex justify-end">
        <Button icon={Plus} onClick={() => alert('Data entry form coming soon')}>
          Add Budget Data
        </Button>
      </div>
    </div>
  );

  const renderStaffingTab = () => (
    <div className="space-y-6">
      {/* Controls */}
      <PageControlsContainer>
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Fiscal Year:
          </label>
          <select
            value={selectedFiscalYear}
            onChange={(e) => setSelectedFiscalYear(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            {[2024, 2023, 2022, 2021, 2020].map(year => (
              <option key={year} value={year}>FY {year}</option>
            ))}
          </select>
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={fetchEfficiencyMetrics}>
            Refresh
          </Button>
        </div>
      </PageControlsContainer>

      {/* Efficiency Metrics Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Staffing & Efficiency Metrics - FY {selectedFiscalYear}
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Council
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Staff FTE
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Species
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  $/Species
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  FTE/Species
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  $/FTE
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {efficiencyMetrics.length > 0 ? (
                efficiencyMetrics.map((metric, idx) => (
                  <tr
                    key={idx}
                    className={`hover:bg-gray-50 dark:hover:bg-gray-900 ${
                      metric.councilCode === 'SAFMC' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                    }`}
                  >
                    <td className="px-4 py-3 whitespace-nowrap font-medium text-gray-900 dark:text-white">
                      {metric.councilCode}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-gray-900 dark:text-white">
                      {formatNumber(metric.staffFte)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-gray-900 dark:text-white">
                      {metric.managedSpecies || 'N/A'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-gray-900 dark:text-white">
                      {formatCurrency(metric.budgetPerSpecies)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-gray-900 dark:text-white">
                      {formatNumber(metric.ftePerSpecies, 2)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-gray-900 dark:text-white">
                      {formatCurrency(metric.budgetPerFte)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                    No efficiency metrics available for FY {selectedFiscalYear}. Add budget, staffing, and workload data.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Staffing Data Button */}
      <div className="flex justify-end">
        <Button icon={Plus} onClick={() => alert('Data entry form coming soon')}>
          Add Staffing Data
        </Button>
      </div>
    </div>
  );

  const renderDataCollectionTab = () => {
    const statusCounts = {
      'Not Started': dataSources.filter(s => s.collectionStatus === 'Not Started').length,
      'In Progress': dataSources.filter(s => s.collectionStatus === 'In Progress').length,
      'Completed': dataSources.filter(s => s.collectionStatus === 'Completed').length,
      'Verified': dataSources.filter(s => s.collectionStatus === 'Verified').length
    };

    const getStatusIcon = (status) => {
      switch (status) {
        case 'Completed':
        case 'Verified':
          return <CheckCircle2 className="h-5 w-5 text-green-500" />;
        case 'In Progress':
          return <Clock className="h-5 w-5 text-yellow-500" />;
        default:
          return <AlertCircle className="h-5 w-5 text-gray-400" />;
      }
    };

    const getStatusVariant = (status) => {
      switch (status) {
        case 'Verified':
        case 'Completed':
          return 'success';
        case 'In Progress':
          return 'warning';
        default:
          return 'neutral';
      }
    };

    const getPriorityVariant = (priority) => {
      switch (priority) {
        case 'Tier 1':
          return 'error';
        case 'Tier 2':
          return 'warning';
        default:
          return 'info';
      }
    };

    return (
      <div className="space-y-6">
        {/* Status Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Object.entries(statusCounts).map(([status, count]) => (
            <div
              key={status}
              className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="text-sm text-gray-600 dark:text-gray-400">{status}</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{count}</div>
            </div>
          ))}
        </div>

        {/* Data Sources List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Data Sources ({dataSources.length})
            </h3>
            <Button icon={Plus} size="sm" onClick={() => alert('Add data source form coming soon')}>
              Add Source
            </Button>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {dataSources.length > 0 ? (
              dataSources.map((source) => (
                <div key={source.id} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-900">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(source.collectionStatus)}
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                          {source.sourceName}
                        </h4>
                        <StatusBadge variant={getPriorityVariant(source.priority)} size="sm">
                          {source.priority}
                        </StatusBadge>
                        <StatusBadge variant={getStatusVariant(source.collectionStatus)} size="sm">
                          {source.collectionStatus}
                        </StatusBadge>
                      </div>
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {source.sourceType && <span>Type: {source.sourceType}</span>}
                        {source.fiscalYears && source.fiscalYears.length > 0 && (
                          <span className="ml-4">
                            Years: {source.fiscalYears.join(', ')}
                          </span>
                        )}
                        {source.councilsCovered && source.councilsCovered.length > 0 && (
                          <span className="ml-4">
                            Councils: {source.councilsCovered.join(', ')}
                          </span>
                        )}
                      </div>
                      {source.sourceUrl && (
                        <a
                          href={source.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-2 inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          <ExternalLink className="h-3 w-3" />
                          View Source
                        </a>
                      )}
                      {source.notes && (
                        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                          {source.notes}
                        </p>
                      )}
                    </div>
                    <div className="ml-4 text-right">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {source.percentComplete}%
                      </div>
                      <div className="mt-1 w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{ width: `${source.percentComplete}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                No data sources added yet. Click "Add Source" to get started.
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderDocumentsTab = () => (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Analysis Documents
          </h3>
          <Button icon={Plus} size="sm" onClick={() => alert('Upload document form coming soon')}>
            Upload Document
          </Button>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {documents.length > 0 ? (
            documents.map((doc) => (
              <div key={doc.id} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-900">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                        {doc.title}
                      </h4>
                      {doc.documentType && (
                        <StatusBadge variant="info" size="sm">
                          {doc.documentType}
                        </StatusBadge>
                      )}
                    </div>
                    {doc.description && (
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {doc.description}
                      </p>
                    )}
                    {doc.tags && doc.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {doc.tags.map((tag, idx) => (
                          <StatusBadge key={idx} variant="neutral" size="sm">
                            {tag}
                          </StatusBadge>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="ml-4 flex gap-2">
                    {doc.filePath && (
                      <Button
                        variant="outline"
                        size="sm"
                        icon={Download}
                        onClick={() => window.open(doc.filePath, '_blank')}
                      >
                        Download
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
              No documents uploaded yet. Upload analysis frameworks, reports, and data templates.
            </div>
          )}
        </div>
      </div>

      {/* Placeholder documents */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border-2 border-blue-500 dark:border-blue-600">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
          Available Documents on Desktop
        </h4>
        <ul className="space-y-2 text-sm text-gray-900 dark:text-gray-100" role="list">
          <li className="flex items-center gap-2 pl-7">
            <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            SAFMC_Resource_Allocation_Analysis_Framework.docx
          </li>
          <li className="flex items-center gap-2 pl-7">
            <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            SAFMC_Resource_Analysis_Strategic_Implications.docx
          </li>
          <li className="flex items-center gap-2 pl-7">
            <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            SAFMC_Resource_Allocation_Data_Collection.xlsx
          </li>
          <li className="flex items-center gap-2 pl-7">
            <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            SAFMC_Resource_Analysis_Quick_Reference.md
          </li>
        </ul>
        <p className="mt-3 text-xs text-gray-700 dark:text-gray-300 pl-7">
          These files are ready to be uploaded to the document repository for team access.
        </p>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-500 mx-auto" />
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading resource allocation data...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Description */}
      <div className="page-description-container">
        <p className="page-description-text">
          Comparative analysis of budget and staffing allocation across all regional fishery management councils to identify resource disparities.
        </p>
        <div className="page-description-actions">
          {isDatabaseInitialized ? (
            <div className="flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-gray-800 rounded-lg border border-green-600 dark:border-green-500">
              <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" aria-hidden="true" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                Database Ready ({councils.length} councils)
              </span>
            </div>
          ) : (
            <Button
              variant="outline"
              icon={Database}
              onClick={runMigration}
            >
              Run Migration
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-8" role="tablist" aria-label="Resource allocation analysis sections">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'budget', label: 'Budget Analysis', icon: DollarSign },
            { id: 'staffing', label: 'Staffing & Metrics', icon: Users },
            { id: 'data-collection', label: 'Data Collection', icon: Database },
            { id: 'documents', label: 'Documents', icon: FileText }
          ].map((tab) => (
            <button
              key={tab.id}
              id={`${tab.id}-tab`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`${tab.id}-panel`}
              tabIndex={activeTab === tab.id ? 0 : -1}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }
              `}
            >
              <tab.icon className="h-5 w-5" aria-hidden="true" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && (
          <div id="overview-panel" role="tabpanel" aria-labelledby="overview-tab" tabIndex={0}>
            {renderOverviewTab()}
          </div>
        )}
        {activeTab === 'budget' && (
          <div id="budget-panel" role="tabpanel" aria-labelledby="budget-tab" tabIndex={0}>
            {renderBudgetTab()}
          </div>
        )}
        {activeTab === 'staffing' && (
          <div id="staffing-panel" role="tabpanel" aria-labelledby="staffing-tab" tabIndex={0}>
            {renderStaffingTab()}
          </div>
        )}
        {activeTab === 'data-collection' && (
          <div id="data-collection-panel" role="tabpanel" aria-labelledby="data-collection-tab" tabIndex={0}>
            {renderDataCollectionTab()}
          </div>
        )}
        {activeTab === 'documents' && (
          <div id="documents-panel" role="tabpanel" aria-labelledby="documents-tab" tabIndex={0}>
            {renderDocumentsTab()}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResourceAllocation;
