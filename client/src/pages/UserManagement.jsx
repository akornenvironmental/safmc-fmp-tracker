/**
 * UserManagement Page
 *
 * Comprehensive user management interface for super admins.
 * Features inline editing for roles, invitation status management, and action menu.
 */

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  Search,
  X,
  Mail,
  Shield,
  UserCheck,
  AlertCircle,
  Building2,
  Send,
  MoreVertical,
  UserX,
  UserPlus,
  Check
} from 'lucide-react';

const UserManagement = () => {
  const { isSuperAdmin } = useAuth();
  const navigate = useNavigate();

  // State
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'
  const [selectedUser, setSelectedUser] = useState(null);

  // Inline editing state
  const [editingRole, setEditingRole] = useState(null);
  const [editingInvitation, setEditingInvitation] = useState(null);
  const [savingField, setSavingField] = useState(null);

  // Action menu state
  const [openActionMenu, setOpenActionMenu] = useState(null);
  const actionMenuRef = useRef(null);

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    organization: '',
    role: 'editor'
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Check permissions
  useEffect(() => {
    if (!isSuperAdmin()) {
      navigate('/');
    }
  }, [isSuperAdmin, navigate]);

  // Fetch users
  useEffect(() => {
    fetchUsers();
  }, []);

  // Close action menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (actionMenuRef.current && !actionMenuRef.current.contains(event.target)) {
        setOpenActionMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch users');
      }

      setUsers(data.users || []);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filter users
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (user.name && user.name.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  // Open create modal
  const handleCreate = () => {
    setModalMode('create');
    setFormData({
      email: '',
      name: '',
      organization: '',
      role: 'editor'
    });
    setFormErrors({});
    setSelectedUser(null);
    setShowModal(true);
  };

  // Open edit modal
  const handleEdit = (user) => {
    setModalMode('edit');
    setFormData({
      email: user.email,
      name: user.name || '',
      organization: user.organization || '',
      role: user.role
    });
    setFormErrors({});
    setSelectedUser(user);
    setShowModal(true);
    setOpenActionMenu(null);
  };

  // Close modal
  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedUser(null);
    setFormData({ email: '', name: '', organization: '', role: 'editor' });
    setFormErrors({});
  };

  // Validate form
  const validateForm = () => {
    const errors = {};

    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email format';
    }

    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }

    if (!['super_admin', 'admin', 'editor'].includes(formData.role)) {
      errors.role = 'Invalid role selected';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('authToken');

      const url = modalMode === 'create'
        ? `${API_BASE_URL}/api/admin/users`
        : `${API_BASE_URL}/api/admin/users/${selectedUser.id}`;

      const method = modalMode === 'create' ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to save user');
      }

      // Success
      await fetchUsers();
      handleCloseModal();

    } catch (err) {
      console.error('Error saving user:', err);
      setFormErrors({ submit: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  // Inline update role
  const handleUpdateRole = async (userId, newRole) => {
    if (!newRole || savingField) return;

    try {
      setSavingField(`role-${userId}`);
      const token = localStorage.getItem('authToken');

      const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role: newRole })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update role');
      }

      // Update local state
      setUsers(users.map(u => u.id === userId ? data.user : u));
      setEditingRole(null);

    } catch (err) {
      console.error('Error updating role:', err);
      alert(`Error: ${err.message}`);
    } finally {
      setSavingField(null);
    }
  };

  // Delete user
  const handleDelete = async (userId, userEmail) => {
    if (!confirm(`Are you sure you want to permanently delete ${userEmail}? This cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('authToken');

      const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to delete user');
      }

      // Success
      await fetchUsers();
      setOpenActionMenu(null);

    } catch (err) {
      console.error('Error deleting user:', err);
      alert(`Error: ${err.message}`);
    }
  };

  // Suspend/Activate user
  const handleToggleSuspend = async (userId, currentStatus, userEmail) => {
    const newStatus = !currentStatus;
    const action = newStatus ? 'activate' : 'suspend';

    if (!confirm(`Are you sure you want to ${action} ${userEmail}?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('authToken');

      const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/suspend`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: newStatus })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Failed to ${action} user`);
      }

      // Update local state
      setUsers(users.map(u => u.id === userId ? data.user : u));
      setOpenActionMenu(null);

    } catch (err) {
      console.error(`Error ${action}ing user:`, err);
      alert(`Error: ${err.message}`);
    }
  };

  // Resend invite
  const handleResendInvite = async (userId, userEmail) => {
    try {
      const token = localStorage.getItem('authToken');

      const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/resend-invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send invite');
      }

      alert(`Invite email sent to ${userEmail}`);
      setOpenActionMenu(null);

    } catch (err) {
      console.error('Error sending invite:', err);
      alert(`Error: ${err.message}`);
    }
  };

  // Get role badge color
  const getRoleBadgeClass = (role) => {
    switch (role) {
      case 'super_admin':
        return 'bg-purple-700 text-white dark:bg-purple-600 dark:text-white';
      case 'admin':
        return 'bg-blue-700 text-white dark:bg-blue-600 dark:text-white';
      case 'editor':
        return 'bg-gray-600 text-white dark:bg-gray-500 dark:text-white';
      default:
        return 'bg-gray-600 text-white dark:bg-gray-500 dark:text-white';
    }
  };

  // Get role display name
  const getRoleDisplayName = (role) => {
    switch (role) {
      case 'super_admin':
        return 'Super Admin';
      case 'admin':
        return 'Admin';
      case 'editor':
        return 'Editor';
      default:
        return role;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div className="sm:flex-auto">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-brand-blue" />
            <div>
              <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-white">User Management</h1>
              <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                Manage user accounts and permissions
              </p>
            </div>
          </div>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={handleCreate}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2"
          >
            <Plus className="w-4 h-4" />
            Add User
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error loading users</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by email or name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Role Filter */}
          <div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Roles</option>
              <option value="super_admin">Super Admin</option>
              <option value="admin">Admin</option>
              <option value="editor">Editor</option>
            </select>
          </div>
        </div>

        {/* Results count */}
        <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredUsers.length} of {users.length} users
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                User
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Organization
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Role
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Invitation
              </th>
              <th className="px-3 py-2 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {filteredUsers.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                  <Users className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p>No users found</p>
                  {searchQuery && (
                    <p className="text-sm mt-1">Try adjusting your search or filters</p>
                  )}
                </td>
              </tr>
            ) : (
              filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-150">
                  {/* User Info */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-brand-blue to-blue-600 flex items-center justify-center text-white font-semibold">
                          {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">{user.name || 'No name'}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{user.email}</div>
                      </div>
                    </div>
                  </td>

                  {/* Organization */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {user.organization || '-'}
                    </span>
                  </td>

                  {/* Role - Inline Editable */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    {editingRole === user.id ? (
                      <div className="flex items-center gap-2">
                        <select
                          value={user.role}
                          onChange={(e) => handleUpdateRole(user.id, e.target.value)}
                          disabled={savingField === `role-${user.id}`}
                          className="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="editor">Editor</option>
                          <option value="admin">Admin</option>
                          <option value="super_admin">Super Admin</option>
                        </select>
                        <button
                          onClick={() => setEditingRole(null)}
                          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setEditingRole(user.id)}
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeClass(user.role)} hover:opacity-80 transition-opacity`}
                      >
                        {getRoleDisplayName(user.role)}
                        <Edit2 className="w-3 h-3 ml-1 opacity-60" />
                      </button>
                    )}
                  </td>

                  {/* Status */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {user.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </td>

                  {/* Invitation Status */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    {user.invitation_status === 'accepted' ? (
                      <div className="flex flex-col">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          <Check className="w-3 h-3 mr-1" />
                          Accepted
                        </span>
                        {user.invitation_accepted_at && (
                          <span className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                            {new Date(user.invitation_accepted_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                        Pending
                      </span>
                    )}
                  </td>

                  {/* Actions Menu */}
                  <td className="px-3 py-3 whitespace-nowrap text-center">
                    <div className="relative inline-block" ref={openActionMenu === user.id ? actionMenuRef : null}>
                      <button
                        onClick={() => setOpenActionMenu(openActionMenu === user.id ? null : user.id)}
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>

                      {openActionMenu === user.id && (
                        <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-10">
                          <div className="py-1">
                            <button
                              onClick={() => handleResendInvite(user.id, user.email)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                            >
                              <Send className="w-4 h-4 mr-3 text-green-600 dark:text-green-400" />
                              Send Invite Email
                            </button>

                            <button
                              onClick={() => handleEdit(user)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                            >
                              <Edit2 className="w-4 h-4 mr-3 text-blue-600 dark:text-blue-400" />
                              Edit User Details
                            </button>

                            <button
                              onClick={() => handleToggleSuspend(user.id, user.is_active, user.email)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                            >
                              {user.is_active ? (
                                <>
                                  <UserX className="w-4 h-4 mr-3 text-orange-600 dark:text-orange-400" />
                                  Suspend User
                                </>
                              ) : (
                                <>
                                  <UserPlus className="w-4 h-4 mr-3 text-green-600 dark:text-green-400" />
                                  Activate User
                                </>
                              )}
                            </button>

                            <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>

                            <button
                              onClick={() => handleDelete(user.id, user.email)}
                              className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                            >
                              <Trash2 className="w-4 h-4 mr-3" />
                              Delete User
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {modalMode === 'create' ? 'Add New User' : 'Edit User'}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSubmit} className="px-6 py-4">
              {/* Email */}
              <div className="mb-4">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    id="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    disabled={modalMode === 'edit'}
                    className={`w-full pl-10 pr-4 py-2 border rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      formErrors.email ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                    } ${modalMode === 'edit' ? 'bg-gray-100 dark:bg-gray-900 cursor-not-allowed' : ''}`}
                    placeholder="user@example.com"
                  />
                </div>
                {formErrors.email && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{formErrors.email}</p>
                )}
              </div>

              {/* Name */}
              <div className="mb-4">
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <UserCheck className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className={`w-full pl-10 pr-4 py-2 border rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      formErrors.name ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder="Full name"
                  />
                </div>
                {formErrors.name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{formErrors.name}</p>
                )}
              </div>

              {/* Organization */}
              <div className="mb-4">
                <label htmlFor="organization" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Organization
                </label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    id="organization"
                    value={formData.organization}
                    onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Company or organization"
                  />
                </div>
              </div>

              {/* Role */}
              <div className="mb-4">
                <label htmlFor="role" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Role <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Shield className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <select
                    id="role"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className={`w-full pl-10 pr-4 py-2 border rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      formErrors.role ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <option value="editor">Editor</option>
                    <option value="admin">Admin</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </div>
                {formErrors.role && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{formErrors.role}</p>
                )}
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {formData.role === 'super_admin' && 'Full system access including user management'}
                  {formData.role === 'admin' && 'Can view activity logs and manage content'}
                  {formData.role === 'editor' && 'Can view and manage FMP tracking data'}
                </p>
              </div>

              {/* Submit Error */}
              {formErrors.submit && (
                <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-3 py-2 rounded-md text-sm">
                  {formErrors.submit}
                </div>
              )}

              {/* Modal Footer */}
              <div className="flex items-center justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-blue"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-brand-blue border border-transparent rounded-md hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-blue disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Saving...' : (modalMode === 'create' ? 'Create User' : 'Save Changes')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
