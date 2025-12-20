/**
 * CMOD Workshops
 * Browse and view CMOD workshop details
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Calendar, Users, MapPin, FileText, ExternalLink, ChevronLeft } from 'lucide-react';
import { API_BASE_URL } from '../../config';
import { toast } from 'react-toastify';
import StatusBadge from '../../components/StatusBadge';

const CMODWorkshops = () => {
  const { id } = useParams();
  const [workshop, setWorkshop] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchWorkshopDetails();
    }
  }, [id]);

  const fetchWorkshopDetails = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/cmod/workshops/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch workshop details');
      }

      const data = await response.json();
      setWorkshop(data.workshop);
      setSessions(data.sessions || []);
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Error fetching workshop:', err);
      toast.error('Failed to load workshop details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusVariant = (status) => {
    const variants = {
      'completed': 'success',
      'scheduled': 'info',
      'cancelled': 'error'
    };
    return variants[status] || 'info';
  };

  const getStatusLabel = (status) => {
    const labels = {
      'completed': 'Completed',
      'scheduled': 'Scheduled',
      'cancelled': 'Cancelled'
    };
    return labels[status] || 'Scheduled';
  };

  const getSessionTypeVariant = (type) => {
    const variants = {
      'Presentation': 'info',
      'Panel': 'purple',
      'Discussion': 'success',
      'Skills Training': 'warning'
    };
    return variants[type] || 'neutral';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue"></div>
      </div>
    );
  }

  if (!workshop) {
    return (
      <div className="text-center py-12">
        <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Workshop Not Found</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          The workshop you're looking for doesn't exist.
        </p>
        <Link
          to="/cmod"
          className="inline-flex items-center gap-2 text-brand-blue hover:text-brand-blue-dark"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to CMOD Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Back Button */}
      <Link
        to="/cmod"
        className="inline-flex items-center gap-2 text-brand-blue hover:text-brand-blue-dark mb-6 transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        Back to CMOD Dashboard
      </Link>

      {/* Workshop Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl font-bold text-brand-blue">{workshop.year}</span>
            <StatusBadge variant={getStatusVariant(workshop.status)} size="md">
              {getStatusLabel(workshop.status)}
            </StatusBadge>
          </div>
          {workshop.materials_url && (
            <a
              href={workshop.materials_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-brand-blue text-white rounded-md hover:bg-brand-blue-dark transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              View Materials
            </a>
          )}
        </div>

        <h1 className="font-heading text-2xl font-bold text-gray-900 dark:text-white mb-3">
          {workshop.title}
        </h1>

        <div className="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-brand-blue p-4 mb-4">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
            <span className="font-semibold">Theme:</span> {workshop.theme}
          </p>
        </div>

        {workshop.description && (
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            {workshop.description}
          </p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <Calendar className="w-5 h-5 text-brand-blue" />
            <div>
              <div className="text-sm font-medium">Date</div>
              <div className="text-sm">
                {workshop.start_date ? new Date(workshop.start_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) : 'TBD'}
                {workshop.end_date && ` - ${new Date(workshop.end_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`}
              </div>
            </div>
          </div>

          {workshop.location && (
            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <MapPin className="w-5 h-5 text-brand-blue" />
              <div>
                <div className="text-sm font-medium">Location</div>
                <div className="text-sm">{workshop.location}</div>
              </div>
            </div>
          )}

          {workshop.host_council && (
            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <Users className="w-5 h-5 text-brand-blue" />
              <div>
                <div className="text-sm font-medium">Host Council</div>
                <div className="text-sm">{workshop.host_council}</div>
              </div>
            </div>
          )}
        </div>

        {workshop.focus_areas && workshop.focus_areas.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Focus Areas</h3>
            <div className="flex flex-wrap gap-2">
              {workshop.focus_areas.map((area, idx) => (
                <StatusBadge key={idx} variant="info" size="sm">
                  {area}
                </StatusBadge>
              ))}
            </div>
          </div>
        )}

        {workshop.skills_components && workshop.skills_components.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Skills Components</h3>
            <div className="flex flex-wrap gap-2">
              {workshop.skills_components.map((skill, idx) => (
                <StatusBadge key={idx} variant="success" size="sm">
                  {skill}
                </StatusBadge>
              ))}
            </div>
          </div>
        )}

        {workshop.participating_councils && workshop.participating_councils.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Participating Councils ({workshop.participating_councils.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {workshop.participating_councils.map((council, idx) => (
                <StatusBadge key={idx} variant="neutral" size="sm">
                  {council}
                </StatusBadge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Workshop Sessions */}
      {sessions.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="font-heading text-xl font-bold text-gray-900 dark:text-white">
              Workshop Sessions ({sessions.length})
            </h2>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {sessions.map((session, idx) => (
              <div key={session.id} className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-semibold text-brand-blue">#{session.session_order || idx + 1}</span>
                    <StatusBadge variant={getSessionTypeVariant(session.session_type)} size="sm">
                      {session.session_type}
                    </StatusBadge>
                  </div>
                  {session.session_date && (
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {new Date(session.session_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  )}
                </div>

                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{session.title}</h3>

                {session.description && (
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{session.description}</p>
                )}

                {session.topics && session.topics.length > 0 && (
                  <div className="mb-3">
                    <div className="flex flex-wrap gap-2">
                      {session.topics.map((topic, idx) => (
                        <StatusBadge key={idx} variant="neutral" size="sm">
                          {topic}
                        </StatusBadge>
                      ))}
                    </div>
                  </div>
                )}

                {session.speakers && session.speakers.length > 0 && (
                  <div className="text-sm">
                    <span className="font-medium text-gray-700 dark:text-gray-300">Speakers: </span>
                    <span className="text-gray-600 dark:text-gray-400">
                      {session.speakers.map((speaker, idx) => (
                        <span key={idx}>
                          {speaker.name}
                          {speaker.affiliation && ` (${speaker.affiliation})`}
                          {idx < session.speakers.length - 1 && ', '}
                        </span>
                      ))}
                    </span>
                  </div>
                )}

                {session.key_takeaways && session.key_takeaways.length > 0 && (
                  <div className="mt-3 bg-gray-50 dark:bg-gray-700/50 rounded p-3">
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Key Takeaways</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                      {session.key_takeaways.map((takeaway, idx) => (
                        <li key={idx}>{takeaway}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Outcomes */}
      {workshop.key_outcomes && Object.keys(workshop.key_outcomes).length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="font-heading text-xl font-bold text-gray-900 dark:text-white">
              Key Outcomes
            </h2>
          </div>
          <div className="p-6">
            <dl className="space-y-3">
              {Object.entries(workshop.key_outcomes).map(([key, value], idx) => (
                <div key={idx}>
                  <dt className="text-sm font-semibold text-gray-700 dark:text-gray-300 capitalize">
                    {key.replace(/_/g, ' ')}
                  </dt>
                  <dd className="text-sm text-gray-600 dark:text-gray-400 mt-1">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {workshop.recommendations && workshop.recommendations.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="font-heading text-xl font-bold text-gray-900 dark:text-white">
              Recommendations
            </h2>
          </div>
          <div className="p-6">
            <ul className="space-y-2">
              {workshop.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-brand-blue mt-1">•</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default CMODWorkshops;
