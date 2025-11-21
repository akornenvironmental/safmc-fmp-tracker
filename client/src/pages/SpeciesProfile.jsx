import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import {
  ArrowLeft, Fish, Calendar, Clock, FileText,
  ExternalLink, ChevronRight, AlertCircle
} from 'lucide-react';

const SpeciesProfile = () => {
  const { speciesName } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Decode the species name from URL
  const decodedName = useMemo(() => {
    return speciesName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }, [speciesName]);

  useEffect(() => {
    fetchSpeciesProfile();
  }, [speciesName]);

  const fetchSpeciesProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/api/species/${encodeURIComponent(speciesName)}`);
      const data = await response.json();

      if (data.success) {
        setProfile(data.species);
      } else {
        setError(data.error || 'Species not found');
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching species profile:', err);
      setError('Failed to load species profile');
      setLoading(false);
    }
  };

  // Get status badge color
  const getStatusColor = (status) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('approved')) return 'bg-green-100 text-green-800';
    if (statusLower.includes('comment')) return 'bg-blue-100 text-blue-800';
    if (statusLower.includes('scoping')) return 'bg-yellow-100 text-yellow-800';
    if (statusLower.includes('hearing')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-800';
  };

  // Get FMP badge color
  const getFMPColor = (fmp) => {
    const colors = {
      'Snapper Grouper': 'bg-blue-100 text-blue-800',
      'Coastal Migratory Pelagics': 'bg-purple-100 text-purple-800',
      'Dolphin Wahoo': 'bg-cyan-100 text-cyan-800',
      'Spiny Lobster': 'bg-red-100 text-red-800',
      'Golden Crab': 'bg-yellow-100 text-yellow-800',
      'Shrimp': 'bg-pink-100 text-pink-800',
      'Coral': 'bg-orange-100 text-orange-800',
      'Sargassum': 'bg-green-100 text-green-800',
    };
    return colors[fmp] || 'bg-gray-100 text-gray-800';
  };

  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading species profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-red-800 mb-2">Species Not Found</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/species')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
          >
            <ArrowLeft size={16} />
            Back to Species List
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="mb-6">
        <ol className="flex items-center space-x-2 text-sm">
          <li>
            <Link to="/species" className="text-gray-500 hover:text-brand-blue">
              Species
            </Link>
          </li>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <li className="text-gray-900 font-medium">{profile.name}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-brand-blue/10 p-3 rounded-lg">
              <Fish className="h-8 w-8 text-brand-blue" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{profile.name}</h1>
              <p className="mt-1 text-gray-500">{profile.summary}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/species')}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft size={16} />
            Back
          </button>
        </div>

        {/* FMP Tags */}
        <div className="mt-4 flex flex-wrap gap-2">
          {profile.fmps?.map(fmp => (
            <span
              key={fmp}
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getFMPColor(fmp)}`}
            >
              {fmp}
            </span>
          ))}
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-brand-blue">{profile.actionCount}</div>
            <div className="text-sm text-gray-500">Total Actions</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">
              {profile.statusBreakdown?.['Approved'] || 0}
            </div>
            <div className="text-sm text-gray-500">Approved</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-900">
              {formatDate(profile.firstMention)}
            </div>
            <div className="text-sm text-gray-500">First Tracked</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-900">
              {formatDate(profile.lastMention)}
            </div>
            <div className="text-sm text-gray-500">Last Tracked</div>
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      {profile.statusBreakdown && Object.keys(profile.statusBreakdown).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Status Breakdown</h2>
          <div className="flex flex-wrap gap-3">
            {Object.entries(profile.statusBreakdown).map(([status, count]) => (
              <div
                key={status}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${getStatusColor(status)}`}
              >
                <span className="font-semibold">{count}</span>
                <span>{status || 'Unknown'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-gray-400" />
          Management Timeline
        </h2>

        {profile.timeline?.length > 0 ? (
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            {/* Timeline items */}
            <div className="space-y-6">
              {profile.timeline.map((item, index) => (
                <div key={item.id || index} className="relative pl-10">
                  {/* Timeline dot */}
                  <div className={`absolute left-2.5 w-3 h-3 rounded-full border-2 ${
                    item.status?.toLowerCase().includes('approved')
                      ? 'bg-green-500 border-green-500'
                      : item.status?.toLowerCase().includes('comment')
                      ? 'bg-blue-500 border-blue-500'
                      : 'bg-gray-300 border-gray-300'
                  }`}></div>

                  <div className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900">
                          {item.source_url ? (
                            <a
                              href={item.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-brand-blue inline-flex items-center gap-1"
                            >
                              {item.title}
                              <ExternalLink size={14} />
                            </a>
                          ) : (
                            item.title
                          )}
                        </h3>
                        {item.description && (
                          <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                            {item.description}
                          </p>
                        )}
                        <div className="mt-2 flex flex-wrap items-center gap-2">
                          {item.status && (
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(item.status)}`}>
                              {item.status}
                            </span>
                          )}
                          {item.fmp && (
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getFMPColor(item.fmp)}`}>
                              {item.fmp}
                            </span>
                          )}
                          {item.type && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                              {item.type}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex-shrink-0 text-right">
                        {item.start_date && (
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <Clock size={12} />
                            {formatDate(item.start_date)}
                          </div>
                        )}
                        {item.progress !== undefined && item.progress !== null && (
                          <div className="mt-1">
                            <div className="w-16 bg-gray-200 rounded-full h-1.5">
                              <div
                                className="bg-brand-blue h-1.5 rounded-full"
                                style={{ width: `${item.progress}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-500">{item.progress}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No timeline data available for this species</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SpeciesProfile;
