import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import { RefreshCw, Download, Settings, RotateCcw, X, BarChart3, Users, MapPin, FileText, ChevronDown, ChevronUp, Sparkles, Brain, Loader2, Fish, Tag } from 'lucide-react';

const CommentsEnhanced = () => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('commentDate');
  const [sortDirection, setSortDirection] = useState('desc');
  const [pageSize, setPageSize] = useState(20);
  const [currentPage, setCurrentPage] = useState(1);
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [selectedComments, setSelectedComments] = useState(new Set());
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [profileType, setProfileType] = useState(null); // 'contact' or 'organization'
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [showDashboard, setShowDashboard] = useState(true);

  // AI Analysis state
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);
  const [analysisFilter, setAnalysisFilter] = useState({ fmp: '', position: '', state: '' });

  // Species detection state
  const [detectingSpecies, setDetectingSpecies] = useState(false);
  const [speciesStats, setSpeciesStats] = useState(null);

  // Dashboard filter state (click-to-filter)
  const [activeFilters, setActiveFilters] = useState({ fmp: '', position: '', state: '', commenterType: '', species: '' });

  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState({
    name: true,
    actionFmp: true,
    actionTitle: true,
    organization: true,
    state: true,
    position: false,
    speciesMentioned: false,
    commentDate: true,
    commentText: true,
  });

  // Define all available columns
  const allColumns = [
    { key: 'name', label: 'Name', core: true },
    { key: 'actionFmp', label: 'FMP', core: false },
    { key: 'actionTitle', label: 'Action/Amendment', core: false },
    { key: 'organization', label: 'Affiliation', core: false },
    { key: 'state', label: 'State', core: false },
    { key: 'position', label: 'Position', core: false },
    { key: 'speciesMentioned', label: 'Species', core: false },
    { key: 'commentDate', label: 'Date', core: true },
    { key: 'commentText', label: 'Comment', core: false },
  ];

  useEffect(() => {
    fetchComments();
    fetchSpeciesStats();
  }, []);

  const fetchSpeciesStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/species-stats`);
      const data = await response.json();
      if (data.success) {
        setSpeciesStats(data);
      }
    } catch (error) {
      console.error('Error fetching species stats:', error);
    }
  };

  const detectSpecies = async () => {
    try {
      setDetectingSpecies(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/comments/detect-species`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();

      if (data.success) {
        alert(`Species detection complete! Updated ${data.updated} comments. Found species in ${data.with_species} comments.`);
        fetchComments(); // Refresh comments with new species data
        fetchSpeciesStats(); // Refresh stats
      } else {
        alert('Species detection failed: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error detecting species:', error);
      alert('Error running species detection');
    } finally {
      setDetectingSpecies(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/comments`);
      const data = await response.json();

      if (data.success) {
        setComments(data.comments || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching comments:', error);
      setLoading(false);
    }
  };

  const syncComments = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/comments`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchComments();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing comments:', error);
      alert('Error syncing comments');
    } finally {
      setSyncing(false);
    }
  };

  // Reset all filters and sorting
  const handleReset = () => {
    setSearchTerm('');
    setSortField('commentDate');
    setSortDirection('desc');
    setCurrentPage(1);
    setSelectedComments(new Set());
    setActiveFilters({ fmp: '', position: '', state: '', commenterType: '', species: '' });
    setShowColumnSelector(false);
  };

  // Handle sorting
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Filter and sort comments
  const filteredAndSortedComments = useMemo(() => {
    // Apply dashboard filters first
    let filtered = comments.filter(comment => {
      if (activeFilters.fmp && comment.actionFmp !== activeFilters.fmp) return false;
      if (activeFilters.position && comment.position !== activeFilters.position) return false;
      if (activeFilters.state && comment.state !== activeFilters.state) return false;
      if (activeFilters.commenterType && comment.commenterType !== activeFilters.commenterType) return false;
      if (activeFilters.species) {
        const species = comment.speciesMentioned || [];
        if (!species.some(s => s.toLowerCase().includes(activeFilters.species.toLowerCase()))) return false;
      }
      return true;
    });

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(comment => (
        comment.name?.toLowerCase().includes(searchLower) ||
        comment.organization?.toLowerCase().includes(searchLower) ||
        comment.position?.toLowerCase().includes(searchLower) ||
        comment.commentText?.toLowerCase().includes(searchLower) ||
        comment.actionFmp?.toLowerCase().includes(searchLower) ||
        comment.actionTitle?.toLowerCase().includes(searchLower)
      ));
    }

    // Then sort
    return [...filtered].sort((a, b) => {
      let aVal = a[sortField] || '';
      let bVal = b[sortField] || '';

      // Handle date sorting
      if (sortField === 'commentDate') {
        aVal = new Date(aVal || 0).getTime();
        bVal = new Date(bVal || 0).getTime();
      } else if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal ? bVal.toLowerCase() : '';
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [comments, searchTerm, sortField, sortDirection, activeFilters]);

  // Export comments to CSV
  const exportToCSV = () => {
    const dataToExport = filteredAndSortedComments;
    if (dataToExport.length === 0) {
      alert('No comments to export');
      return;
    }

    const headers = ['Name', 'Organization', 'Email', 'City', 'State', 'FMP', 'Action', 'Position', 'Commenter Type', 'Species Mentioned', 'Date', 'Comment'];
    const rows = dataToExport.map(c => [
      c.name || '',
      c.organization || '',
      c.email || '',
      c.city || '',
      c.state || '',
      c.actionFmp || '',
      c.actionTitle || '',
      c.position || '',
      c.commenterType || '',
      (c.speciesMentioned || []).join('; '),
      c.commentDate ? new Date(c.commentDate).toLocaleDateString() : '',
      (c.commentText || '').replace(/"/g, '""') // Escape quotes
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `safmc-comments-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Toggle dashboard filter
  const toggleFilter = (filterType, value) => {
    setActiveFilters(prev => ({
      ...prev,
      [filterType]: prev[filterType] === value ? '' : value
    }));
    setCurrentPage(1);
  };

  // Check if any filters are active
  const hasActiveFilters = Object.values(activeFilters).some(v => v !== '');

  // Pagination
  const paginatedComments = useMemo(() => {
    if (pageSize >= 999999) return filteredAndSortedComments;
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedComments.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedComments, currentPage, pageSize]);

  const totalPages = pageSize >= 999999 ? 1 : Math.ceil(filteredAndSortedComments.length / pageSize);

  // Compute dashboard analytics
  const dashboardStats = useMemo(() => {
    if (comments.length === 0) return null;

    const stats = {
      total: comments.length,
      byPosition: {},
      byCommenterType: {},
      byState: {},
      byFmp: {},
      recentComments: 0,
      topOrganizations: []
    };

    // Count comments from last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const orgCounts = {};

    comments.forEach(comment => {
      // By position
      const position = comment.position || 'Neutral';
      stats.byPosition[position] = (stats.byPosition[position] || 0) + 1;

      // By commenter type
      const type = comment.commenterType || 'Unknown';
      stats.byCommenterType[type] = (stats.byCommenterType[type] || 0) + 1;

      // By state
      if (comment.state) {
        stats.byState[comment.state] = (stats.byState[comment.state] || 0) + 1;
      }

      // By FMP
      if (comment.actionFmp) {
        stats.byFmp[comment.actionFmp] = (stats.byFmp[comment.actionFmp] || 0) + 1;
      }

      // Recent comments
      if (comment.commentDate) {
        const commentDate = new Date(comment.commentDate);
        if (commentDate >= thirtyDaysAgo) {
          stats.recentComments++;
        }
      }

      // Organization counts
      if (comment.organization) {
        orgCounts[comment.organization] = (orgCounts[comment.organization] || 0) + 1;
      }
    });

    // Get top 5 organizations
    stats.topOrganizations = Object.entries(orgCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([name, count]) => ({ name, count }));

    return stats;
  }, [comments]);

  // Toggle selection
  const toggleSelectComment = (comment) => {
    const newSelected = new Set(selectedComments);
    if (newSelected.has(comment.id)) {
      newSelected.delete(comment.id);
    } else {
      newSelected.add(comment.id);
    }
    setSelectedComments(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedComments.size === paginatedComments.length) {
      setSelectedComments(new Set());
    } else {
      setSelectedComments(new Set(paginatedComments.map(c => c.id)));
    }
  };

  // Helper to get columns that should be displayed
  const getDisplayColumns = () => {
    return allColumns.filter(col => {
      if (col.key === 'name' || col.key === 'commentDate') return true;
      return visibleColumns[col.key];
    });
  };

  const toggleColumn = (columnKey) => {
    if (columnKey === 'name' || columnKey === 'commentDate') return;
    const column = allColumns.find(col => col.key === columnKey);
    if (column && !column.core) {
      setVisibleColumns(prev => ({
        ...prev,
        [columnKey]: !prev[columnKey]
      }));
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Profile modal functions
  const fetchContactProfile = async (contactId) => {
    try {
      setLoadingProfile(true);
      const response = await fetch(`${API_BASE_URL}/api/contacts/${contactId}`);
      const data = await response.json();
      if (data.success) {
        setProfileData(data.contact);
        setProfileType('contact');
        setShowProfileModal(true);
      }
    } catch (error) {
      console.error('Error fetching contact:', error);
    } finally {
      setLoadingProfile(false);
    }
  };

  const fetchOrganizationProfile = async (orgId) => {
    try {
      setLoadingProfile(true);
      const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}`);
      const data = await response.json();
      if (data.success) {
        setProfileData(data.organization);
        setProfileType('organization');
        setShowProfileModal(true);
      }
    } catch (error) {
      console.error('Error fetching organization:', error);
    } finally {
      setLoadingProfile(false);
    }
  };

  const closeProfileModal = () => {
    setShowProfileModal(false);
    setProfileData(null);
    setProfileType(null);
  };

  // AI Analysis functions
  const runAIAnalysis = async () => {
    try {
      setAnalyzing(true);
      setAnalysisError(null);
      setAnalysisResult(null);

      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/ai/analyze-comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          fmp: analysisFilter.fmp || undefined,
          position: analysisFilter.position || undefined,
          state: analysisFilter.state || undefined
        })
      });

      const data = await response.json();

      if (data.success) {
        setAnalysisResult(data);
      } else {
        setAnalysisError(data.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Error running AI analysis:', error);
      setAnalysisError('Failed to connect to AI service');
    } finally {
      setAnalyzing(false);
    }
  };

  const closeAnalysisModal = () => {
    setShowAnalysisModal(false);
    setAnalysisResult(null);
    setAnalysisError(null);
  };

  // Get unique values for filter dropdowns
  const uniqueFmps = useMemo(() => {
    const fmps = new Set(comments.map(c => c.actionFmp).filter(Boolean));
    return Array.from(fmps).sort();
  }, [comments]);

  const uniquePositions = useMemo(() => {
    const positions = new Set(comments.map(c => c.position).filter(Boolean));
    return Array.from(positions).sort();
  }, [comments]);

  const uniqueStates = useMemo(() => {
    const states = new Set(comments.map(c => c.state).filter(Boolean));
    return Array.from(states).sort();
  }, [comments]);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        if (showAnalysisModal) closeAnalysisModal();
        else if (showProfileModal) closeProfileModal();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [showProfileModal, showAnalysisModal]);

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-gray-100">Public Comments</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Showing {filteredAndSortedComments.length} of {comments.length} comments
          </p>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Comments are automatically synced weekly from SAFMC public hearings and comment periods.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 flex flex-wrap gap-2">
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-slate-300 dark:border-slate-600 bg-gradient-to-r from-slate-50 to-gray-50 dark:from-slate-800 dark:to-gray-800 px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 shadow-sm hover:from-slate-100 hover:to-gray-100 dark:hover:from-slate-700 dark:hover:to-gray-700 hover:border-slate-400 transition-all"
            title="Reset filters, sorting, and selection"
          >
            <RotateCcw size={14} />
            Reset
          </button>
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-indigo-300 dark:border-indigo-600 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 px-3 py-1.5 text-xs font-medium text-indigo-700 dark:text-indigo-300 shadow-sm hover:from-indigo-100 hover:to-purple-100 dark:hover:from-indigo-900/50 dark:hover:to-purple-900/50 hover:border-indigo-400 transition-all"
          >
            <Settings size={14} />
            Columns
          </button>
          <button
            onClick={syncComments}
            disabled={syncing}
            className={`inline-flex items-center gap-1.5 justify-center rounded-md border px-3 py-1.5 text-xs font-medium shadow-sm transition-all ${
              syncing
                ? 'border-gray-300 bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'border-emerald-300 bg-gradient-to-r from-emerald-50 to-teal-50 text-emerald-700 hover:from-emerald-100 hover:to-teal-100 hover:border-emerald-400'
            }`}
          >
            <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
            {syncing ? 'Syncing...' : 'Sync Comments'}
          </button>
          <button
            onClick={() => setShowAnalysisModal(true)}
            disabled={comments.length === 0}
            className={`inline-flex items-center gap-1.5 justify-center rounded-md border px-3 py-1.5 text-xs font-medium shadow-sm transition-all ${
              comments.length === 0
                ? 'border-gray-300 bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'border-violet-300 dark:border-violet-600 bg-gradient-to-r from-violet-50 to-fuchsia-50 dark:from-violet-900/30 dark:to-fuchsia-900/30 text-violet-700 dark:text-violet-300 hover:from-violet-100 hover:to-fuchsia-100 dark:hover:from-violet-900/50 dark:hover:to-fuchsia-900/50 hover:border-violet-400'
            }`}
          >
            <Sparkles size={14} />
            AI Analysis
          </button>
          <button
            onClick={detectSpecies}
            disabled={detectingSpecies || comments.length === 0}
            className={`inline-flex items-center gap-1.5 justify-center rounded-md border px-3 py-1.5 text-xs font-medium shadow-sm transition-all ${
              detectingSpecies || comments.length === 0
                ? 'border-gray-300 bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'border-teal-300 dark:border-teal-600 bg-gradient-to-r from-teal-50 to-emerald-50 dark:from-teal-900/30 dark:to-emerald-900/30 text-teal-700 dark:text-teal-300 hover:from-teal-100 hover:to-emerald-100 dark:hover:from-teal-900/50 dark:hover:to-emerald-900/50 hover:border-teal-400'
            }`}
          >
            <Fish size={14} className={detectingSpecies ? 'animate-pulse' : ''} />
            {detectingSpecies ? 'Detecting...' : 'Detect Species'}
          </button>
          <button
            onClick={exportToCSV}
            disabled={filteredAndSortedComments.length === 0}
            className={`inline-flex items-center gap-1.5 justify-center rounded-md border px-3 py-1.5 text-xs font-medium shadow-sm transition-all ${
              filteredAndSortedComments.length === 0
                ? 'border-gray-300 bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'border-sky-300 dark:border-sky-600 bg-gradient-to-r from-sky-50 to-cyan-50 dark:from-sky-900/30 dark:to-cyan-900/30 text-sky-700 dark:text-sky-300 hover:from-sky-100 hover:to-cyan-100 dark:hover:from-sky-900/50 dark:hover:to-cyan-900/50 hover:border-sky-400'
            }`}
          >
            <Download size={14} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Active Filters Indicator */}
      {hasActiveFilters && (
        <div className="mt-4 flex items-center gap-2 flex-wrap">
          <span className="text-xs text-gray-500 dark:text-gray-400">Active filters:</span>
          {activeFilters.fmp && (
            <button
              onClick={() => toggleFilter('fmp', activeFilters.fmp)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-xs hover:bg-blue-200 dark:hover:bg-blue-800"
            >
              FMP: {activeFilters.fmp}
              <X size={12} />
            </button>
          )}
          {activeFilters.position && (
            <button
              onClick={() => toggleFilter('position', activeFilters.position)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 rounded-full text-xs hover:bg-green-200 dark:hover:bg-green-800"
            >
              Position: {activeFilters.position}
              <X size={12} />
            </button>
          )}
          {activeFilters.state && (
            <button
              onClick={() => toggleFilter('state', activeFilters.state)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 rounded-full text-xs hover:bg-amber-200 dark:hover:bg-amber-800"
            >
              State: {activeFilters.state}
              <X size={12} />
            </button>
          )}
          {activeFilters.commenterType && (
            <button
              onClick={() => toggleFilter('commenterType', activeFilters.commenterType)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 rounded-full text-xs hover:bg-purple-200 dark:hover:bg-purple-800"
            >
              Type: {activeFilters.commenterType}
              <X size={12} />
            </button>
          )}
          {activeFilters.species && (
            <button
              onClick={() => toggleFilter('species', activeFilters.species)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-teal-100 dark:bg-teal-900/50 text-teal-700 dark:text-teal-300 rounded-full text-xs hover:bg-teal-200 dark:hover:bg-teal-800"
            >
              <Fish size={10} />
              Species: {activeFilters.species}
              <X size={12} />
            </button>
          )}
          <button
            onClick={() => setActiveFilters({ fmp: '', position: '', state: '', commenterType: '', species: '' })}
            className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 underline"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Dashboard Section */}
      {dashboardStats && (
        <div className="mt-6">
          <button
            onClick={() => setShowDashboard(!showDashboard)}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-brand-blue dark:hover:text-brand-blue-light transition-colors mb-3"
          >
            <BarChart3 size={18} />
            Comment Analytics Dashboard
            {showDashboard ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {showDashboard && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Total Comments Card */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
                    <FileText className="text-blue-600 dark:text-blue-300" size={20} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{dashboardStats.total}</p>
                    <p className="text-xs text-blue-600 dark:text-blue-400">Total Comments</p>
                  </div>
                </div>
                <div className="mt-3 text-xs text-blue-700 dark:text-blue-300">
                  {dashboardStats.recentComments} in last 30 days
                </div>
              </div>

              {/* Position Breakdown Card */}
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/30 dark:to-teal-900/30 rounded-lg p-4 border border-emerald-200 dark:border-emerald-800">
                <div className="flex items-center gap-2 mb-3">
                  <div className="p-2 bg-emerald-100 dark:bg-emerald-800 rounded-lg">
                    <BarChart3 className="text-emerald-600 dark:text-emerald-300" size={20} />
                  </div>
                  <p className="text-sm font-medium text-emerald-900 dark:text-emerald-100">By Position</p>
                </div>
                <div className="space-y-1.5">
                  {Object.entries(dashboardStats.byPosition)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 4)
                    .map(([position, count]) => (
                      <button
                        key={position}
                        onClick={() => toggleFilter('position', position)}
                        className={`w-full flex justify-between items-center hover:opacity-80 transition-opacity ${activeFilters.position === position ? 'ring-2 ring-emerald-500 rounded' : ''}`}
                      >
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          position.toLowerCase().includes('support') ? 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300' :
                          position.toLowerCase().includes('oppose') ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300' :
                          'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                        }`}>
                          {position}
                        </span>
                        <span className="text-xs font-medium text-emerald-800 dark:text-emerald-200">{count}</span>
                      </button>
                    ))}
                </div>
              </div>

              {/* Commenter Type Card */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
                <div className="flex items-center gap-2 mb-3">
                  <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
                    <Users className="text-purple-600 dark:text-purple-300" size={20} />
                  </div>
                  <p className="text-sm font-medium text-purple-900 dark:text-purple-100">By Sector</p>
                </div>
                <div className="space-y-1.5">
                  {Object.entries(dashboardStats.byCommenterType)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 4)
                    .map(([type, count]) => (
                      <button
                        key={type}
                        onClick={() => toggleFilter('commenterType', type)}
                        className={`w-full flex justify-between items-center hover:opacity-80 transition-opacity ${activeFilters.commenterType === type ? 'ring-2 ring-purple-500 rounded' : ''}`}
                      >
                        <span className="text-xs text-purple-700 dark:text-purple-300 truncate max-w-[120px]">{type}</span>
                        <span className="text-xs font-medium text-purple-800 dark:text-purple-200">{count}</span>
                      </button>
                    ))}
                </div>
              </div>

              {/* Top States Card */}
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
                <div className="flex items-center gap-2 mb-3">
                  <div className="p-2 bg-amber-100 dark:bg-amber-800 rounded-lg">
                    <MapPin className="text-amber-600 dark:text-amber-300" size={20} />
                  </div>
                  <p className="text-sm font-medium text-amber-900 dark:text-amber-100">Top States</p>
                </div>
                <div className="space-y-1.5">
                  {Object.entries(dashboardStats.byState)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 4)
                    .map(([state, count]) => (
                      <button
                        key={state}
                        onClick={() => toggleFilter('state', state)}
                        className={`w-full flex justify-between items-center hover:opacity-80 transition-opacity ${activeFilters.state === state ? 'ring-2 ring-amber-500 rounded' : ''}`}
                      >
                        <span className="text-xs text-amber-700 dark:text-amber-300">{state}</span>
                        <span className="text-xs font-medium text-amber-800 dark:text-amber-200">{count}</span>
                      </button>
                    ))}
                </div>
              </div>

              {/* FMP Breakdown - Full Width */}
              {Object.keys(dashboardStats.byFmp).length > 0 && (
                <div className="md:col-span-2 bg-gradient-to-br from-slate-50 to-gray-50 dark:from-slate-900/50 dark:to-gray-900/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-3">Comments by FMP <span className="text-xs font-normal text-slate-500">(click to filter)</span></p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(dashboardStats.byFmp)
                      .sort((a, b) => b[1] - a[1])
                      .map(([fmp, count]) => (
                        <button
                          key={fmp}
                          onClick={() => toggleFilter('fmp', fmp)}
                          className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors ${activeFilters.fmp === fmp ? 'border-blue-500 ring-2 ring-blue-500' : 'border-slate-200 dark:border-slate-600'}`}
                        >
                          {fmp}
                          <span className="font-medium text-slate-900 dark:text-slate-100">{count}</span>
                        </button>
                      ))}
                  </div>
                </div>
              )}

              {/* Top Organizations */}
              {dashboardStats.topOrganizations.length > 0 && (
                <div className="md:col-span-2 bg-gradient-to-br from-cyan-50 to-sky-50 dark:from-cyan-900/30 dark:to-sky-900/30 rounded-lg p-4 border border-cyan-200 dark:border-cyan-800">
                  <p className="text-sm font-medium text-cyan-900 dark:text-cyan-100 mb-3">Top Commenting Organizations</p>
                  <div className="space-y-2">
                    {dashboardStats.topOrganizations.map(({ name, count }, idx) => (
                      <div key={name} className="flex justify-between items-center">
                        <span className="text-xs text-cyan-700 dark:text-cyan-300 truncate max-w-[300px]">
                          {idx + 1}. {name}
                        </span>
                        <span className="text-xs font-medium bg-cyan-100 dark:bg-cyan-800 text-cyan-800 dark:text-cyan-200 px-2 py-0.5 rounded">
                          {count} comments
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Species Mentioned - Click to filter */}
              {speciesStats && speciesStats.top_species && speciesStats.top_species.length > 0 && (
                <div className="md:col-span-2 lg:col-span-4 bg-gradient-to-br from-teal-50 to-emerald-50 dark:from-teal-900/30 dark:to-emerald-900/30 rounded-lg p-4 border border-teal-200 dark:border-teal-800">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Fish className="text-teal-600 dark:text-teal-300" size={18} />
                      <p className="text-sm font-medium text-teal-900 dark:text-teal-100">
                        Species Mentioned in Comments
                        <span className="text-xs font-normal text-teal-600 dark:text-teal-400 ml-2">
                          ({speciesStats.comments_with_species} of {speciesStats.total_comments} comments)
                        </span>
                      </p>
                    </div>
                    <span className="text-xs text-teal-600 dark:text-teal-400">(click to filter)</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {speciesStats.top_species.slice(0, 15).map(({ species, count }) => (
                      <button
                        key={species}
                        onClick={() => toggleFilter('species', species)}
                        className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-teal-100 dark:bg-teal-800 text-teal-700 dark:text-teal-300 border hover:bg-teal-200 dark:hover:bg-teal-700 transition-colors ${activeFilters.species === species ? 'border-teal-500 ring-2 ring-teal-500' : 'border-teal-200 dark:border-teal-600'}`}
                      >
                        <Tag size={10} />
                        {species}
                        <span className="font-medium text-teal-900 dark:text-teal-100">{count}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Column selector */}
      {showColumnSelector && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Columns</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {allColumns.map(col => (
              <label key={col.key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={visibleColumns[col.key] || col.key === 'name' || col.key === 'commentDate'}
                  onChange={() => toggleColumn(col.key)}
                  disabled={col.key === 'name' || col.key === 'commentDate'}
                  className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:bg-gray-700"
                />
                <span className={`text-sm ${(col.key === 'name' || col.key === 'commentDate') ? 'text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'}`}>
                  {col.label} {(col.key === 'name' || col.key === 'commentDate') && '(required)'}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Search and page size */}
      <div className="mt-6 flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Search comments..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="flex-1 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border bg-white dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-400"
          aria-label="Search comments by name, organization, position, or comment text"
        />
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border bg-white dark:bg-gray-800 dark:text-gray-100"
          aria-label="Number of comments to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>
      </div>

      {/* Comments Table */}
      <div className="mt-6 bg-white dark:bg-gray-800 shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" className="px-2 py-1.5 text-left">
                <input
                  type="checkbox"
                  checked={selectedComments.size === paginatedComments.length && paginatedComments.length > 0}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:bg-gray-700"
                  aria-label={`Select all ${paginatedComments.length} comments on this page`}
                />
              </th>
              {getDisplayColumns().map(col => (
                <th
                  key={col.key}
                  scope="col"
                  className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 select-none"
                  onClick={() => handleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {sortField === col.key && (
                      <span className="text-blue-600">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">
                  Loading comments...
                </td>
              </tr>
            ) : paginatedComments.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">
                  No comments found
                </td>
              </tr>
            ) : (
              paginatedComments.map((comment, index) => (
                <tr key={comment.id || index} className={`${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'} hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150`}>
                  <td className="px-2 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedComments.has(comment.id)}
                      onChange={() => toggleSelectComment(comment)}
                      className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:bg-gray-700"
                      aria-label={`Select comment from ${comment.name || 'Anonymous'}`}
                    />
                  </td>
                  {getDisplayColumns().map(col => (
                    <td key={col.key} className="px-2 py-0.5">
                      {col.key === 'name' ? (
                        comment.contactId ? (
                          <button
                            onClick={() => fetchContactProfile(comment.contactId)}
                            className="text-xs font-medium text-brand-blue hover:text-brand-green hover:underline cursor-pointer"
                          >
                            {comment.name || 'Anonymous'}
                          </button>
                        ) : (
                          <div className="text-xs font-medium text-gray-900 dark:text-gray-100">{comment.name || 'Anonymous'}</div>
                        )
                      ) : col.key === 'actionFmp' ? (
                        <div className="text-xs text-gray-700 dark:text-gray-300 font-medium">{comment.actionFmp || '—'}</div>
                      ) : col.key === 'actionTitle' ? (
                        <div className="text-xs text-gray-700 dark:text-gray-300 max-w-xs truncate" title={comment.actionTitle || 'No action specified'}>
                          {comment.actionTitle || '—'}
                        </div>
                      ) : col.key === 'organization' ? (
                        comment.organizationId ? (
                          <button
                            onClick={() => fetchOrganizationProfile(comment.organizationId)}
                            className="text-xs text-brand-blue hover:text-brand-green hover:underline cursor-pointer"
                          >
                            {comment.organization || '—'}
                          </button>
                        ) : (
                          <div className="text-xs text-gray-900 dark:text-gray-100 max-w-[150px] truncate" title={comment.organization}>{comment.organization || '—'}</div>
                        )
                      ) : col.key === 'state' ? (
                        <div className="text-xs text-gray-900 dark:text-gray-100">{comment.state || '—'}</div>
                      ) : col.key === 'position' ? (
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          comment.position?.toLowerCase().includes('support') ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200' :
                          comment.position?.toLowerCase().includes('oppose') ? 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200' :
                          'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                        }`}>
                          {comment.position || 'Neutral'}
                        </span>
                      ) : col.key === 'speciesMentioned' ? (
                        <div className="flex flex-wrap gap-1 max-w-[200px]">
                          {comment.speciesMentioned && comment.speciesMentioned.length > 0 ? (
                            comment.speciesMentioned.slice(0, 3).map((sp, idx) => (
                              <button
                                key={idx}
                                onClick={() => toggleFilter('species', sp)}
                                className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-teal-100 dark:bg-teal-900/50 text-teal-700 dark:text-teal-300 rounded text-[10px] hover:bg-teal-200 dark:hover:bg-teal-800"
                              >
                                <Fish size={8} />
                                {sp}
                              </button>
                            ))
                          ) : (
                            <span className="text-xs text-gray-400">—</span>
                          )}
                          {comment.speciesMentioned && comment.speciesMentioned.length > 3 && (
                            <span className="text-[10px] text-teal-600 dark:text-teal-400">+{comment.speciesMentioned.length - 3}</span>
                          )}
                        </div>
                      ) : col.key === 'commentDate' ? (
                        <div className="text-xs text-gray-700 dark:text-gray-300">{formatDate(comment.commentDate)}</div>
                      ) : col.key === 'commentText' ? (
                        <div className="text-xs text-gray-700 dark:text-gray-300 max-w-md truncate" title={comment.commentText}>{comment.commentText || '—'}</div>
                      ) : null}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Profile Modal */}
      {showProfileModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={closeProfileModal}
        >
          <div
            className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="profile-modal-title"
          >
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
              <h2 id="profile-modal-title" className="font-heading text-2xl font-bold text-gray-900 dark:text-gray-100">
                {profileType === 'contact' ? 'Contact Profile' : 'Organization Profile'}
              </h2>
              <button
                onClick={closeProfileModal}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                aria-label="Close profile modal"
              >
                <X size={24} />
              </button>
            </div>

            <div className="px-6 py-4">
              {loadingProfile ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading...</div>
              ) : profileData ? (
                profileType === 'contact' ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Name</h3>
                      <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.name || '—'}</p>
                    </div>
                    {profileData.email && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Email</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">
                          <a href={`mailto:${profileData.email}`} className="text-brand-blue hover:text-brand-green hover:underline">
                            {profileData.email}
                          </a>
                        </p>
                      </div>
                    )}
                    {profileData.phone && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Phone</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.phone}</p>
                      </div>
                    )}
                    {(profileData.city || profileData.state) && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Location</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">
                          {[profileData.city, profileData.state].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    )}
                    {profileData.affiliation && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Affiliation</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.affiliation}</p>
                      </div>
                    )}
                    {profileData.comment_count > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Comments</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.comment_count}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Organization Name</h3>
                      <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.name || '—'}</p>
                    </div>
                    {profileData.type && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Type</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.type}</p>
                      </div>
                    )}
                    {(profileData.city || profileData.state) && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Location</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">
                          {[profileData.city, profileData.state].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    )}
                    {profileData.website && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Website</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">
                          <a
                            href={profileData.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-blue hover:text-brand-green hover:underline"
                          >
                            {profileData.website}
                          </a>
                        </p>
                      </div>
                    )}
                    {profileData.description && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Description</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.description}</p>
                      </div>
                    )}
                    {profileData.comment_count > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Comments</h3>
                        <p className="mt-1 text-base text-gray-900 dark:text-gray-100">{profileData.comment_count}</p>
                      </div>
                    )}
                  </div>
                )
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">No profile data available</div>
              )}
            </div>

            <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
              <button
                onClick={closeProfileModal}
                className="w-full px-4 py-2 bg-brand-blue text-white rounded-md hover:bg-brand-blue-light transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Analysis Modal */}
      {showAnalysisModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={closeAnalysisModal}
        >
          <div
            className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="analysis-modal-title"
          >
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-violet-100 dark:bg-violet-900/50 rounded-lg">
                  <Brain className="text-violet-600 dark:text-violet-300" size={24} />
                </div>
                <div>
                  <h2 id="analysis-modal-title" className="font-heading text-xl font-bold text-gray-900 dark:text-gray-100">
                    AI Comment Analysis
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Powered by Claude AI
                  </p>
                </div>
              </div>
              <button
                onClick={closeAnalysisModal}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                aria-label="Close analysis modal"
              >
                <X size={24} />
              </button>
            </div>

            <div className="px-6 py-4">
              {/* Filters */}
              {!analysisResult && !analyzing && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Filter Comments (Optional)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">FMP</label>
                      <select
                        value={analysisFilter.fmp}
                        onChange={(e) => setAnalysisFilter(prev => ({ ...prev, fmp: e.target.value }))}
                        className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                      >
                        <option value="">All FMPs</option>
                        {uniqueFmps.map(fmp => (
                          <option key={fmp} value={fmp}>{fmp}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Position</label>
                      <select
                        value={analysisFilter.position}
                        onChange={(e) => setAnalysisFilter(prev => ({ ...prev, position: e.target.value }))}
                        className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                      >
                        <option value="">All Positions</option>
                        {uniquePositions.map(pos => (
                          <option key={pos} value={pos}>{pos}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">State</label>
                      <select
                        value={analysisFilter.state}
                        onChange={(e) => setAnalysisFilter(prev => ({ ...prev, state: e.target.value }))}
                        className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm text-gray-900 dark:text-gray-100"
                      >
                        <option value="">All States</option>
                        {uniqueStates.map(state => (
                          <option key={state} value={state}>{state}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <button
                    onClick={runAIAnalysis}
                    disabled={analyzing}
                    className="mt-4 w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-lg font-medium hover:from-violet-700 hover:to-fuchsia-700 transition-all shadow-lg shadow-violet-500/25"
                  >
                    <Sparkles size={18} />
                    Analyze {comments.length} Comments with AI
                  </button>
                </div>
              )}

              {/* Loading State */}
              {analyzing && (
                <div className="text-center py-12">
                  <Loader2 size={48} className="animate-spin text-violet-600 dark:text-violet-400 mx-auto mb-4" />
                  <p className="text-gray-700 dark:text-gray-300 font-medium">Analyzing comments...</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    This may take 15-30 seconds depending on the number of comments
                  </p>
                </div>
              )}

              {/* Error State */}
              {analysisError && (
                <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
                  <p className="text-red-700 dark:text-red-300 font-medium">Analysis Failed</p>
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">{analysisError}</p>
                  <button
                    onClick={() => {
                      setAnalysisError(null);
                      setAnalysisResult(null);
                    }}
                    className="mt-3 text-sm text-red-700 dark:text-red-300 underline hover:no-underline"
                  >
                    Try again
                  </button>
                </div>
              )}

              {/* Results */}
              {analysisResult && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between bg-violet-50 dark:bg-violet-900/30 rounded-lg p-3 mb-4">
                    <span className="text-sm text-violet-700 dark:text-violet-300">
                      Analyzed {analysisResult.comments_analyzed} of {analysisResult.total_comments} comments
                    </span>
                    <button
                      onClick={() => {
                        setAnalysisResult(null);
                        setAnalysisFilter({ fmp: '', position: '', state: '' });
                      }}
                      className="text-sm text-violet-600 dark:text-violet-400 hover:underline"
                    >
                      New Analysis
                    </button>
                  </div>

                  {/* Analysis Content - Rendered as Markdown-like */}
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 whitespace-pre-wrap text-gray-800 dark:text-gray-200 text-sm leading-relaxed">
                      {analysisResult.answer}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
              <button
                onClick={closeAnalysisModal}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommentsEnhanced;
