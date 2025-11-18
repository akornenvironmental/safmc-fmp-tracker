import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import { RefreshCw, Download, Settings, RotateCcw, X } from 'lucide-react';

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

  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState({
    name: true,
    actionFmp: true,
    actionTitle: true,
    organization: true,
    state: true,
    position: false,
    commentDate: true,
    comment_text: true,
  });

  // Define all available columns
  const allColumns = [
    { key: 'name', label: 'Name', core: true },
    { key: 'actionFmp', label: 'FMP', core: false },
    { key: 'actionTitle', label: 'Action/Amendment', core: false },
    { key: 'organization', label: 'Affiliation', core: false },
    { key: 'state', label: 'State', core: false },
    { key: 'position', label: 'Position', core: false },
    { key: 'commentDate', label: 'Date', core: true },
    { key: 'comment_text', label: 'Comment', core: false },
  ];

  useEffect(() => {
    fetchComments();
  }, []);

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
    // Apply search filter
    const filtered = comments.filter(comment => {
      const searchLower = searchTerm.toLowerCase();
      return (
        comment.name?.toLowerCase().includes(searchLower) ||
        comment.organization?.toLowerCase().includes(searchLower) ||
        comment.position?.toLowerCase().includes(searchLower) ||
        comment.comment_text?.toLowerCase().includes(searchLower) ||
        comment.actionFmp?.toLowerCase().includes(searchLower) ||
        comment.actionTitle?.toLowerCase().includes(searchLower)
      );
    });

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
  }, [comments, searchTerm, sortField, sortDirection]);

  // Pagination
  const paginatedComments = useMemo(() => {
    if (pageSize >= 999999) return filteredAndSortedComments;
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedComments.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedComments, currentPage, pageSize]);

  const totalPages = pageSize >= 999999 ? 1 : Math.ceil(filteredAndSortedComments.length / pageSize);

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

  // Handle ESC key to close modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && showProfileModal) {
        closeProfileModal();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [showProfileModal]);

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Public Comments</h1>
          <p className="mt-2 text-sm text-gray-700">
            Showing {filteredAndSortedComments.length} of {comments.length} comments
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Comments are automatically synced weekly from SAFMC public hearings and comment periods.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 flex flex-wrap gap-2">
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-slate-300 bg-gradient-to-r from-slate-50 to-gray-50 px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm hover:from-slate-100 hover:to-gray-100 hover:border-slate-400 transition-all"
            title="Reset filters, sorting, and selection"
          >
            <RotateCcw size={14} />
            Reset
          </button>
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-indigo-300 bg-gradient-to-r from-indigo-50 to-purple-50 px-3 py-1.5 text-xs font-medium text-indigo-700 shadow-sm hover:from-indigo-100 hover:to-purple-100 hover:border-indigo-400 transition-all"
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
        </div>
      </div>

      {/* Column selector */}
      {showColumnSelector && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Columns</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {allColumns.map(col => (
              <label key={col.key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={visibleColumns[col.key] || col.key === 'name' || col.key === 'commentDate'}
                  onChange={() => toggleColumn(col.key)}
                  disabled={col.key === 'name' || col.key === 'commentDate'}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className={`text-sm ${(col.key === 'name' || col.key === 'commentDate') ? 'text-gray-400' : 'text-gray-700'}`}>
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
          className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border bg-white"
          aria-label="Search comments by name, organization, position, or comment text"
        />
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border bg-white"
          aria-label="Number of comments to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>
      </div>

      {/* Comments Table */}
      <div className="mt-6 bg-white shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-2 py-1.5 text-left">
                <input
                  type="checkbox"
                  checked={selectedComments.size === paginatedComments.length && paginatedComments.length > 0}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  aria-label={`Select all ${paginatedComments.length} comments on this page`}
                />
              </th>
              {getDisplayColumns().map(col => (
                <th
                  key={col.key}
                  scope="col"
                  className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
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
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500">
                  Loading comments...
                </td>
              </tr>
            ) : paginatedComments.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500">
                  No comments found
                </td>
              </tr>
            ) : (
              paginatedComments.map((comment, index) => (
                <tr key={comment.id || index} className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-100'} hover:bg-gray-50 transition-colors duration-150`}>
                  <td className="px-2 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedComments.has(comment.id)}
                      onChange={() => toggleSelectComment(comment)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
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
                          <div className="text-xs font-medium text-gray-900">{comment.name || 'Anonymous'}</div>
                        )
                      ) : col.key === 'actionFmp' ? (
                        <div className="text-xs text-gray-700 font-medium">{comment.actionFmp || '—'}</div>
                      ) : col.key === 'actionTitle' ? (
                        <div className="text-xs text-gray-700 max-w-xs truncate" title={comment.actionTitle || 'No action specified'}>
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
                          <div className="text-xs text-gray-700">{comment.organization || '—'}</div>
                        )
                      ) : col.key === 'state' ? (
                        <div className="text-xs text-gray-700">{comment.state || '—'}</div>
                      ) : col.key === 'position' ? (
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          comment.position?.toLowerCase().includes('support') ? 'bg-green-100 text-green-800' :
                          comment.position?.toLowerCase().includes('oppose') ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {comment.position || 'Neutral'}
                        </span>
                      ) : col.key === 'commentDate' ? (
                        <div className="text-xs text-gray-500">{formatDate(comment.commentDate)}</div>
                      ) : col.key === 'comment_text' ? (
                        <div className="text-xs text-gray-600 max-w-md truncate">{comment.comment_text || '—'}</div>
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
          <div className="text-sm text-gray-700">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
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
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="profile-modal-title"
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 id="profile-modal-title" className="font-heading text-2xl font-bold text-gray-900">
                {profileType === 'contact' ? 'Contact Profile' : 'Organization Profile'}
              </h2>
              <button
                onClick={closeProfileModal}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Close profile modal"
              >
                <X size={24} />
              </button>
            </div>

            <div className="px-6 py-4">
              {loadingProfile ? (
                <div className="text-center py-8 text-gray-500">Loading...</div>
              ) : profileData ? (
                profileType === 'contact' ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Name</h3>
                      <p className="mt-1 text-base text-gray-900">{profileData.name || '—'}</p>
                    </div>
                    {profileData.email && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Email</h3>
                        <p className="mt-1 text-base text-gray-900">
                          <a href={`mailto:${profileData.email}`} className="text-brand-blue hover:text-brand-green hover:underline">
                            {profileData.email}
                          </a>
                        </p>
                      </div>
                    )}
                    {profileData.phone && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Phone</h3>
                        <p className="mt-1 text-base text-gray-900">{profileData.phone}</p>
                      </div>
                    )}
                    {(profileData.city || profileData.state) && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Location</h3>
                        <p className="mt-1 text-base text-gray-900">
                          {[profileData.city, profileData.state].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    )}
                    {profileData.affiliation && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Affiliation</h3>
                        <p className="mt-1 text-base text-gray-900">{profileData.affiliation}</p>
                      </div>
                    )}
                    {profileData.comment_count > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Total Comments</h3>
                        <p className="mt-1 text-base text-gray-900">{profileData.comment_count}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Organization Name</h3>
                      <p className="mt-1 text-base text-gray-900">{profileData.name || '—'}</p>
                    </div>
                    {profileData.type && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Type</h3>
                        <p className="mt-1 text-base text-gray-900">{profileData.type}</p>
                      </div>
                    )}
                    {(profileData.city || profileData.state) && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Location</h3>
                        <p className="mt-1 text-base text-gray-900">
                          {[profileData.city, profileData.state].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    )}
                    {profileData.website && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Website</h3>
                        <p className="mt-1 text-base text-gray-900">
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
                        <h3 className="text-sm font-medium text-gray-500">Description</h3>
                        <p className="mt-1 text-base text-gray-900">{profileData.description}</p>
                      </div>
                    )}
                    {profileData.comment_count > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Total Comments</h3>
                        <p className="mt-1 text-base text-gray-900">{profileData.comment_count}</p>
                      </div>
                    )}
                  </div>
                )
              ) : (
                <div className="text-center py-8 text-gray-500">No profile data available</div>
              )}
            </div>

            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
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
    </div>
  );
};

export default CommentsEnhanced;
