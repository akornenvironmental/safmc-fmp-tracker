import { useState, useEffect } from 'react';
import { User, Mail, Building2, Shield, Calendar, Bell } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { API_BASE_URL } from '../config';

const UserProfile = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [userDetails, setUserDetails] = useState(null);
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    notify_new_comments: true,
    notify_weekly_digest: true
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchUserDetails();
  }, []);

  const fetchUserDetails = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserDetails(data.user);
        setPreferences({
          email_notifications: data.user.email_notifications ?? true,
          notify_new_comments: data.user.notify_new_comments ?? true,
          notify_weekly_digest: data.user.notify_weekly_digest ?? true
        });
      }
    } catch (error) {
      console.error('Error fetching user details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/users/preferences`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      });

      if (response.ok) {
        alert('Preferences saved successfully!');
      } else {
        alert('Failed to save preferences');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('Error saving preferences');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  const displayUser = userDetails || user;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">My Profile</h1>

      {/* User Information Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <User className="w-5 h-5" />
          Account Information
        </h2>

        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <User className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Name</div>
              <div className="text-base text-gray-900 dark:text-gray-100">{displayUser?.name || 'Not set'}</div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Email</div>
              <div className="text-base text-gray-900 dark:text-gray-100">{displayUser?.email}</div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Building2 className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Organization</div>
              <div className="text-base text-gray-900 dark:text-gray-100">
                {displayUser?.organization || 'Not set'}
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Role</div>
              <div className="text-base text-gray-900 dark:text-gray-100 capitalize">
                {displayUser?.role?.replace('_', ' ')}
              </div>
            </div>
          </div>

          {displayUser?.last_login && (
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Last Login</div>
                <div className="text-base text-gray-900 dark:text-gray-100">
                  {new Date(displayUser.last_login).toLocaleString()}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Notification Preferences Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notification Preferences
        </h2>

        <div className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={preferences.email_notifications}
              onChange={(e) => setPreferences({ ...preferences, email_notifications: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Email Notifications
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Receive email notifications for updates
              </div>
            </div>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={preferences.notify_new_comments}
              onChange={(e) => setPreferences({ ...preferences, notify_new_comments: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                New Comments
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Get notified when someone comments on items you follow
              </div>
            </div>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={preferences.notify_weekly_digest}
              onChange={(e) => setPreferences({ ...preferences, notify_weekly_digest: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Weekly Digest
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Receive a weekly summary of activity
              </div>
            </div>
          </label>
        </div>

        <div className="mt-6">
          <button
            onClick={handleSavePreferences}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>

      {/* Future Features Note */}
      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Coming Soon:</strong> User favorites/flagging system for research items - You'll be able to flag amendments, assessments, meeting notes, and other items to organize them into custom collections for your research.
        </p>
      </div>
    </div>
  );
};

export default UserProfile;
