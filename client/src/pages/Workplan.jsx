import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import Button from '../components/Button';
import ButtonGroup from '../components/ButtonGroup';
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
  Filter,
  RotateCcw,
  FileText,
  ExternalLink,
  Upload,
  ClipboardList
} from 'lucide-react';

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

  const getMilestoneColor = (type) => {
    const colors = {
      'AR': 'bg-blue-100 text-blue-800 border-blue-300',
      'S': 'bg-purple-100 text-purple-800 border-purple-300',
      'DOC': 'bg-green-100 text-green-800 border-green-300',
      'PH': 'bg-orange-100 text-orange-800 border-orange-300',
      'A': 'bg-emerald-100 text-emerald-800 border-emerald-300',
      'SUBMIT': 'bg-cyan-100 text-cyan-800 border-cyan-300',
      'IMPL': 'bg-teal-100 text-teal-800 border-teal-300'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-300';
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
      {/* Header */}
      <PageHeader
        icon={ClipboardList}
        title="Workplan"
        subtitle="Management priorities"
        description="Council workplan showing current and upcoming management priorities."
      />

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{workplan.version.versionName}</h2>
            <p className="text-sm text-gray-600 mt-1">
              Effective: {new Date(workplan.version.effectiveDate).toLocaleDateString()}
            </p>
            {workplan.version.quarter && (
              <span className="inline-block mt-2 px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                {workplan.version.quarter} {workplan.version.fiscalYear}
              </span>
            )}
          </div>

          <ButtonGroup>
            <Link to="/workplan/upload">
              <Button variant="secondary" icon={Upload}>
                Upload Workplan
              </Button>
            </Link>
            <Button
              variant="secondary"
              icon={History}
              onClick={() => setShowVersionHistory(!showVersionHistory)}
            >
              Version History
            </Button>
            <Button
              variant="primary"
              icon={RefreshCw}
              onClick={fetchWorkplan}
            >
              Refresh
            </Button>
          </ButtonGroup>
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
                      <span className="px-2 py-1 text-xs font-medium bg-green-600 text-white rounded">
                        Current
                      </span>
                    )}
                    {selectedVersionId === version.id && (
                      <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded">
                        Viewing
                      </span>
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
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search amendments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="UNDERWAY">Underway</option>
              <option value="PLANNED">Planned</option>
              <option value="COMPLETED">Completed</option>
              <option value="DEFERRED">Deferred</option>
            </select>
          </div>

          <Button
            variant="secondary"
            icon={RotateCcw}
            onClick={() => {
              setSearchTerm('');
              setSelectedStatus('all');
            }}
          >
            Reset
          </Button>
        </div>
      </div>

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
                              <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                                {item.seroPriority}
                              </span>
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
                                <div className={`px-3 py-1 text-xs font-medium rounded border ${getMilestoneColor(milestone.milestoneType)}`}>
                                  <span className="mr-1">{getMilestoneIcon(milestone.milestoneType)}</span>
                                  {milestone.milestoneType}
                                </div>

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
              <div className={`inline-block px-2 py-1 rounded border ${getMilestoneColor(code)} mb-1`}>
                <span className="mr-1">{getMilestoneIcon(code)}</span>
                {code}
              </div>
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
