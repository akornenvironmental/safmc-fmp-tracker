import { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';
import { API_BASE_URL } from '../config';

/**
 * Reusable Favorite Button Component
 * @param {string} itemType - Type of item (action, meeting, assessment, document, etc.)
 * @param {string} itemId - ID of the item
 * @param {function} onFavoriteChange - Optional callback when favorite status changes
 */
const FavoriteButton = ({ itemType, itemId, onFavoriteChange }) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteId, setFavoriteId] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkFavoriteStatus();
  }, [itemType, itemId]);

  const checkFavoriteStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/user/favorites/check`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: [{ item_type: itemType, item_id: itemId }]
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const key = `${itemType}:${itemId}`;
        const status = data.favorited?.[key];
        if (status) {
          setIsFavorited(status.is_favorited);
          setFavoriteId(status.favorite_id);
        }
      }
    } catch (error) {
      console.error('Error checking favorite status:', error);
    }
  };

  const toggleFavorite = async (e) => {
    e.stopPropagation(); // Prevent triggering parent click events
    setLoading(true);

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        alert('Please log in to use favorites');
        setLoading(false);
        return;
      }

      if (isFavorited && favoriteId) {
        // Remove favorite
        const response = await fetch(`${API_BASE_URL}/api/user/favorites/${favoriteId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          setIsFavorited(false);
          setFavoriteId(null);
          if (onFavoriteChange) onFavoriteChange(false);
        }
      } else {
        // Add favorite
        const response = await fetch(`${API_BASE_URL}/api/user/favorites`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            item_type: itemType,
            item_id: itemId,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          setIsFavorited(true);
          setFavoriteId(data.favorite?.id);
          if (onFavoriteChange) onFavoriteChange(true);
        }
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      alert('Failed to update favorite');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={toggleFavorite}
      disabled={loading}
      className={`p-1.5 rounded-full transition-all ${
        isFavorited
          ? 'text-red-500 hover:bg-red-50'
          : 'text-gray-400 hover:text-red-500 hover:bg-gray-100'
      } ${loading ? 'opacity-50 cursor-wait' : ''}`}
      title={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
    >
      <Heart
        size={18}
        fill={isFavorited ? 'currentColor' : 'none'}
        strokeWidth={2}
      />
    </button>
  );
};

export default FavoriteButton;
