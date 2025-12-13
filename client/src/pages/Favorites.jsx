import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Filter, X, FileText, Calendar, Users, File, Trash2 } from 'lucide-react';
import { API_BASE_URL } from '../config';

const Favorites = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    fetchFavorites();
  }, [filterType]);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        setLoading(false);
        return;
      }

      const url = filterType === 'all'
        ? `${API_BASE_URL}/api/user/favorites`
        : `${API_BASE_URL}/api/user/favorites?type=${filterType}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setFavorites(data.favorites || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching favorites:', error);
      setLoading(false);
    }
  };

  const removeFavorite = async (favoriteId) => {
    if (!confirm('Remove this item from favorites?')) return;

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/user/favorites/${favoriteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setFavorites(favorites.filter(f => f.id !== favoriteId));
      }
    } catch (error) {
      console.error('Error removing favorite:', error);
      alert('Failed to remove favorite');
    }
  };

  const getItemIcon = (type) => {
    const icons = {
      action: FileText,
      meeting: Calendar,
      assessment: Users,
      document: File,
    };
    return icons[type] || FileText;
  };

  const getItemLink = (favorite) => {
    // Generate appropriate link based on item type
    if (favorite.item_type === 'action') {
      return `/actions?id=${favorite.item_id}`;
    } else if (favorite.item_type === 'meeting') {
      return `/meetings?id=${favorite.item_id}`;
    }
    return '#';
  };

  const itemTypes = [
    { value: 'all', label: 'All Items' },
    { value: 'action', label: 'Actions' },
    { value: 'meeting', label: 'Meetings' },
    { value: 'assessment', label: 'Assessments' },
    { value: 'document', label: 'Documents' },
  ];

  if (loading) {
    return (
      <div>
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-600 dark:text-gray-400">Loading favorites...</div>
        </div>
      </div>
    );
  }

  return (
    <div>

      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Heart className="text-red-500" fill="currentColor" />
              My Favorites
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Items you've saved for quick access
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              {itemTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {favorites.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <Heart size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            No favorites yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Start adding items to your favorites by clicking the heart icon on actions, meetings, and other items.
          </p>
          <Link
            to="/actions"
            className="inline-block px-4 py-2 bg-brand-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Browse Actions
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {favorites.map((favorite) => {
            const Icon = getItemIcon(favorite.item_type);
            const item = favorite.item || {};

            return (
              <div
                key={favorite.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <Icon size={20} className="text-gray-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                          {favorite.item_type}
                        </span>
                        {favorite.flagged_as && (
                          <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded">
                            {favorite.flagged_as}
                          </span>
                        )}
                      </div>
                      <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1">
                        {item.title || item.name || favorite.item_id}
                      </h3>
                      {item.fmp && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          FMP: {item.fmp}
                        </p>
                      )}
                      {item.location && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {item.location}
                        </p>
                      )}
                      {favorite.notes && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 italic">
                          Note: {favorite.notes}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                        Added {new Date(favorite.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      to={getItemLink(favorite)}
                      className="px-3 py-1.5 text-sm text-brand-blue hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                    >
                      View
                    </Link>
                    <button
                      onClick={() => removeFavorite(favorite.id)}
                      className="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                      title="Remove from favorites"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {favorites.length > 0 && (
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center">
          Showing {favorites.length} favorite{favorites.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

export default Favorites;
