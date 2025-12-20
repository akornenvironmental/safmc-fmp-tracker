import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import { API_BASE_URL } from '../config';
import {
  RefreshCw,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronRight,
  ChevronDown,
  History,
  RotateCcw,
  FileText,
  ExternalLink,
  Upload
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

const Workplan = () => {
  const [workplan, setWorkplan] = useState(null);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [selectedVersionId, setSelectedVersionId] = useState(null);

  useEffect(() => {
    fetchWorkplan();
    fetchVersions();
  }, []);

  const fetchWorkplan = async (versionId = null) => {
    try {
      setLoading(true);
      const url = versionId
        ? `${API_BASE_URL}/api/workplan/version/${versionId}`
        : `${API_BASE_URL}/api/workplan/current`;
      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        setWorkplan(data);
        setSelectedVersionId(data.version?.id || null);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching workplan:', error);
      setLoading(false);
    }
  };

  const fetchVersions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/workplan/stats`);
      const statsData = await response.json();

      const versionsResponse = await fetch(`${API_BASE_URL}/api/workplan/versions`);
      const data = await versionsResponse.json();

      if (data.success) {
        // Add item counts to versions
        const versionsWithCounts = data.versions || [];
        setVersions(versionsWithCounts);
      }
    } catch (error) {
      console.error('Error fetching versions:', error);
    }
  };

  const handleVersionSelect = (versionId) => {
    setSelectedVersionId(versionId);
    fetchWorkplan(versionId);
    setShowVersionHistory(false);
  };

  const toggleItemExpanded = (itemId) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  // Filter and search items
  const filteredItems = useMemo(() => {
    if (!workplan?.items) return [];

    return workplan.items.filter(item => {
      // Status filter
      if (selectedStatus !== 'all' && item.status !== selectedStatus) {
        return false;
      }

      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          item.amendmentId?.toLowerCase().includes(searchLower) ||
          item.topic?.toLowerCase().includes(searchLower) ||
          item.leadStaff?.toLowerCase().includes(searchLower)
        );
      }

      return true;
    });
  }, [workplan, selectedStatus, searchTerm]);

  // Group items by status
  const itemsByStatus = useMemo(() => {
    const grouped = {
      'UNDERWAY': [],
      'PLANNED': [],
      'COMPLETED': [],
      'DEFERRED': []
    };

    filteredItems.forEach(item => {
      if (grouped[item.status]) {
        grouped[item.status].push(item);
      }
    });

    return grouped;
  }, [filteredItems]);

  const getMilestoneIcon = (type) => {
    const icons = {
      'AR': '📊',
      'S': '🔍',
      'DOC': '📄',
      'PH': '🎤',
      'A': '✅',
      'SUBMIT': '📤',
      'IMPL': '🎯'
    };
    return icons[type] || '📌';
  };

  const getMilestoneVariant = (type) => {
    const variants = {
      'AR': 'info',
      'S': 'purple',
      'DOC': 'success',
      'PH': 'warning',
      'A': 'success',
      'SUBMIT': 'info',
      'IMPL': 'success'
    };
    return variants[type] || 'neutral';
  };

  const getStatusColor = (status) => {
    const colors = {
      'UNDERWAY': 'bg-blue-50 border-blue-200',
      'PLANNED': 'bg-gray-50 border-gray-200',
      'COMPLETED': 'bg-green-50 border-green-200',
      'DEFERRED': 'bg-yellow-50 border-yellow-200'
    };
    return colors[status] || 'bg-gray-50 border-gray-200';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'UNDERWAY': <Clock className="w-4 h-4 text-blue-600" />,
      'PLANNED': <Calendar className="w-4 h-4 text-gray-600" />,
      'COMPLETED': <CheckCircle2 className="w-4 h-4 text-green-600" />,
      'DEFERRED': <AlertCircle className="w-4 h-4 text-yellow-600" />
    };
    return icons[status] || <Calendar className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-gray-600">Loading workplan...</p>
        </div>
      </div>
    );
  }

  if (!workplan?.version) {
    return (
      <div className="p-8 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="text-lg font-semibold text-yellow-900 mb-2">No Active Workplan</h3>
        <p className="text-yellow-700 mb-4">No workplan has been imported yet. Import a workplan file to get started.</p>
        <Link
          to="/workplan/upload"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Upload className="w-4 h-4" />
          Upload Workplan
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Description and Actions */}
      <div className="page-description-container">
        <p className="page-description-text">
          Track and manage the Council's strategic workplan, priorities, and project timelines.
        </p>
        <div className="page-description-actions">
          <Link to="/workplan/upload">
            <Button variant="secondary" icon={Upload} className="gap-1.5 px-2.5 h-9">
              Upload Workplan
            </Button>
          </Link>
          <Button
            variant="secondary"
            icon={History}
            onClick={() => setShowVersionHistory(!showVersionHistory)}
            className="gap-1.5 px-2.5 h-9"
          >
            Version History
          </Button>
          <Button
            variant="primary"
            icon={RefreshCw}
            onClick={fetchWorkplan}
            className="gap-1.5 px-2.5 h-9"
          >
            Refresh
          </Button>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{workplan.version.versionName}</h2>
            <p className="text-sm text-gray-600 mt-1">
              Effective: {new Date(workplan.version.effectiveDate).toLocaleDateString()}
            </p>
            {workplan.version.quarter && (
              <StatusBadge variant="info" size="sm">
                {workplan.version.quarter} {workplan.version.fiscalYear}
              </StatusBadge>
            )}
          </div>
        </div>
      </div>

      {/* Version History Panel */}
      {showVersionHistory && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">All Workplan Versions (Click to view)</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {versions
              .sort((a, b) => new Date(b.effectiveDate) - new Date(a.effectiveDate))
              .map(version => (
              <div
                key={version.id}
                onClick={() => handleVersionSelect(version.id)}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedVersionId === version.id
                    ? 'bg-blue-50 border-blue-400 ring-2 ring-blue-200'
                    : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{version.versionName}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(version.effectiveDate).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {version.isActive && (
                      <StatusBadge variant="success" size="sm">
                        Current
                      </StatusBadge>
                    )}
                    {selectedVersionId === version.id && (
                      <StatusBadge variant="info" size="sm">
                        Viewing
                      </StatusBadge>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats Summary - Clickable to filter */}
      <div className="grid grid-cols-4 gap-4">
        {Object.entries(itemsByStatus).map(([status, items]) => (
          <div
            key={status}
            onClick={() => setSelectedStatus(selectedStatus === status ? 'all' : status)}
            className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${getStatusColor(status)} ${
              selectedStatus === status ? 'ring-2 ring-blue-400 shadow-md' : ''
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              {getStatusIcon(status)}
              <span className="text-sm font-medium text-gray-700">{status}</span>
              {selectedStatus === status && (
                <span className="ml-auto text-xs text-blue-600">(filtered)</span>
              )}
            </div>
            <p className="text-2xl font-bold text-gray-900">{items.length}</p>
          </div>
        ))}
      </div>

      {/* Filters and Search */}
      <PageControlsContainer>
        {/* Search input */}
        <SearchBar
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Search amendments..."
          ariaLabel="Search amendments by ID, topic, or lead staff"
        />

        {/* Status Filter */}
        <FilterDropdown
          label="Status"
          options={[
            { value: 'UNDERWAY', label: 'Underway', count: itemsByStatus['UNDERWAY']?.length || 0 },
            { value: 'PLANNED', label: 'Planned', count: itemsByStatus['PLANNED']?.length || 0 },
            { value: 'COMPLETED', label: 'Completed', count: itemsByStatus['COMPLETED']?.length || 0 },
            { value: 'DEFERRED', label: 'Deferred', count: itemsByStatus['DEFERRED']?.length || 0 }
          ]}
          selectedValues={selectedStatus === 'all' ? [] : [selectedStatus]}
          onChange={(values) => setSelectedStatus(values.length > 0 ? values[0] : 'all')}
          showCounts={true}
        />

        {/* Reset Button */}
        <button
          onClick={() => {
            setSearchTerm('');
            setSelectedStatus('all');
          }}
          className="inline-flex items-center gap-2 h-9 px-3 text-sm font-medium rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-600 hover:bg-red-100 dark:hover:bg-red-900/40 hover:border-red-400 dark:hover:border-red-500 transition-colors"
          title="Reset filters and search"
        >
          <RotateCcw size={14} />
          Reset
        </button>
      </PageControlsContainer>

      {/* Amendments List */}
      <div className="space-y-4">
        {Object.entries(itemsByStatus).map(([status, items]) => (
          items.length > 0 && (
            <div key={status} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className={`px-6 py-3 border-b ${getStatusColor(status)}`}>
                <div className="flex items-center gap-2">
                  {getStatusIcon(status)}
                  <h3 className="font-semibold text-gray-900">{status}</h3>
                  <span className="text-sm text-gray-600">({items.length})</span>
                </div>
              </div>

              <div className="divide-y">
                {items.map(item => (
                  <div key={item.id} className="hover:bg-gray-50">
                    <div
                      className="px-6 py-4 cursor-pointer"
                      onClick={() => toggleItemExpanded(item.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            {expandedItems.has(item.id) ? (
                              <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                            ) : (
                              <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                            )}
                            <span className="font-mono text-sm font-semibold text-blue-600">
                              {item.amendmentId}
                            </span>
                            {item.seroPriority && (
                              <StatusBadge variant="purple" size="sm">
                                {item.seroPriority}
                              </StatusBadge>
                            )}
                          </div>

                          <p className="text-gray-900 font-medium ml-8">{item.topic}</p>

                          {item.leadStaff && (
                            <p className="text-sm text-gray-600 ml-8 mt-1">
                              Lead: {item.leadStaff}
                            </p>
                          )}

                          {item.actionId && (
                            <p className="text-xs text-gray-500 ml-8 mt-1">
                              Linked to: {item.actionId}
                            </p>
                          )}
                        </div>

                        {item.milestones && item.milestones.length > 0 && (
                          <div className="text-sm text-gray-600">
                            {item.milestones.length} milestone{item.milestones.length !== 1 ? 's' : ''}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Expanded Milestones */}
                    {expandedItems.has(item.id) && item.milestones && item.milestones.length > 0 && (
                      <div className="px-6 pb-4 ml-8">
                        <div className="border-l-2 border-gray-200 pl-6 space-y-3">
                          {item.milestones
                            .sort((a, b) => new Date(a.scheduledDate) - new Date(b.scheduledDate))
                            .map((milestone, idx) => (
                              <div key={idx} className="flex items-start gap-3">
                                <StatusBadge variant={getMilestoneVariant(milestone.milestoneType)} size="sm">
                                  <span className="mr-1">{getMilestoneIcon(milestone.milestoneType)}</span>
                                  {milestone.milestoneType}
                                </StatusBadge>

                                <div className="flex-1">
                                  <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1">
                                      <p className="text-sm font-medium text-gray-900">
                                        {milestone.scheduledMeeting}
                                      </p>
                                      <p className="text-xs text-gray-600">
                                        {new Date(milestone.scheduledDate).toLocaleDateString()}
                                      </p>
                                      {milestone.isCompleted && (
                                        <p className="text-xs text-green-600 mt-1">
                                          ✓ Completed {milestone.completedDate ? new Date(milestone.completedDate).toLocaleDateString() : ''}
                                        </p>
                                      )}
                                    </div>
                                    {milestone.meeting && milestone.meeting.sourceUrl && (
                                      <a
                                        href={milestone.meeting.sourceUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-1 px-2 py-1 text-xs text-brand-blue hover:text-blue-700 hover:bg-blue-50 rounded border border-blue-200 hover:border-blue-300 transition-colors"
                                        title="View meeting materials"
                                      >
                                        <FileText size={14} />
                                        <span>Docs</span>
                                        <ExternalLink size={12} />
                                      </a>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )
        ))}
      </div>

      {/* Milestone Legend */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Milestone Legend</h3>
        <div className="grid grid-cols-4 gap-3">
          {[
            { code: 'AR', name: 'Assessment Report', desc: 'Stock assessment presented' },
            { code: 'S', name: 'Scoping', desc: 'Public scoping' },
            { code: 'DOC', name: 'Document Review', desc: 'Review actions/alternatives' },
            { code: 'PH', name: 'Public Hearing', desc: 'Public hearings' },
            { code: 'A', name: 'Approval', desc: 'Final approval' },
            { code: 'SUBMIT', name: 'Submitted', desc: 'Submitted to NMFS' },
            { code: 'IMPL', name: 'Implementation', desc: 'Rule implemented' }
          ].map(({ code, name, desc }) => (
            <div key={code} className="text-xs">
              <StatusBadge variant={getMilestoneVariant(code)} size="sm" className="mb-1">
                <span className="mr-1">{getMilestoneIcon(code)}</span>
                {code}
              </StatusBadge>
              <p className="font-medium text-gray-900">{name}</p>
              <p className="text-gray-600">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Workplan;
