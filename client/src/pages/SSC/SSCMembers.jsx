/**
 * SSC Members Directory
 *
 * Displays the 21 members of the SAFMC Scientific and Statistical Committee
 * with their expertise areas, affiliations, and roles.
 */

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../config';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../../components/PageControls';
import {
  Users,
  Mail,
  Phone,
  Building2,
  Award,
  MapPin,
  Crown,
  Shield,
  AlertCircle
} from 'lucide-react';

const SSCMembers = () => {
  const [members, setMembers] = useState([]);
  const [filteredMembers, setFilteredMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [stateFilter, setStateFilter] = useState([]);
  const [seatTypeFilter, setSeatTypeFilter] = useState([]);

  // Fetch SSC members
  useEffect(() => {
    fetchMembers();
  }, []);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/ssc/members`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch SSC members');
      }

      setMembers(data.members || []);
      setFilteredMembers(data.members || []);
    } catch (err) {
      console.error('Error fetching SSC members:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Apply filters
  useEffect(() => {
    let filtered = [...members];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(member =>
        member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        member.expertise_area?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        member.affiliation?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // State filter
    if (stateFilter.length > 0) {
      filtered = filtered.filter(member => stateFilter.includes(member.state));
    }

    // Seat type filter
    if (seatTypeFilter.length > 0) {
      filtered = filtered.filter(member => seatTypeFilter.includes(member.seat_type));
    }

    setFilteredMembers(filtered);
  }, [searchQuery, stateFilter, seatTypeFilter, members]);

  // Get unique states
  const states = [...new Set(members.map(m => m.state))].filter(Boolean).sort();

  // Get unique seat types
  const seatTypes = [...new Set(members.map(m => m.seat_type))].filter(Boolean).sort();

  // Get role badge
  const getRoleBadge = (member) => {
    if (member.is_chair) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300">
          <Crown className="w-3 h-3" />
          Chair
        </span>
      );
    }
    if (member.is_vice_chair) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
          <Shield className="w-3 h-3" />
          Vice-Chair
        </span>
      );
    }
    return null;
  };

  // Get seat type badge color
  const getSeatTypeBadge = (seatType) => {
    const colors = {
      'At-large': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      'State-designated': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'Economist': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      'Social Scientist': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300'
    };
    return colors[seatType] || 'bg-gray-100 text-gray-800';
  };

  // Get initials for avatar
  const getInitials = (name) => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return parts[0][0] + parts[parts.length - 1][0];
    }
    return name.substring(0, 2);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading SSC members...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Description */}
      <div className="page-description-container">
        <p className="page-description-text">
          Browse the Scientific and Statistical Committee member directory with expertise and contact information.
        </p>
        <div className="page-description-actions"></div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error loading SSC members</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Page Controls */}
      <PageControlsContainer>
        {/* Search Bar */}
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search by name, expertise, or affiliation..."
          ariaLabel="Search SSC members"
        />

        {/* State Filter */}
        <FilterDropdown
          label="State"
          options={states.map(state => ({
            value: state,
            label: state,
            count: members.filter(m => m.state === state).length
          }))}
          selectedValues={stateFilter}
          onChange={setStateFilter}
          showCounts={true}
        />

        {/* Seat Type Filter */}
        <FilterDropdown
          label="Seat Type"
          options={seatTypes.map(type => ({
            value: type,
            label: type,
            count: members.filter(m => m.seat_type === type).length
          }))}
          selectedValues={seatTypeFilter}
          onChange={setSeatTypeFilter}
          showCounts={true}
        />
      </PageControlsContainer>

      {/* Results Count */}
      <div className="mt-6 mb-4 text-sm text-gray-600 dark:text-gray-400">
        Showing {filteredMembers.length} of {members.length} members
      </div>

      {/* Members Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMembers.map((member) => (
          <div
            key={member.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden border border-gray-200 dark:border-gray-700"
          >
            {/* Card Header */}
            <div className="bg-gradient-to-r from-brand-blue to-blue-600 p-4">
              <div className="flex items-center gap-3">
                {/* Avatar */}
                <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
                  {getInitials(member.name)}
                </div>
                {/* Name and Role */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white text-lg truncate">
                    {member.name}
                  </h3>
                  {getRoleBadge(member)}
                </div>
              </div>
            </div>

            {/* Card Body */}
            <div className="p-4 space-y-3">
              {/* Seat Type */}
              <div>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getSeatTypeBadge(member.seat_type)}`}>
                  {member.seat_type}
                </span>
              </div>

              {/* State */}
              {member.state && (
                <div className="flex items-start gap-2 text-sm">
                  <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 dark:text-gray-300">{member.state}</span>
                </div>
              )}

              {/* Expertise */}
              {member.expertise_area && (
                <div className="flex items-start gap-2 text-sm">
                  <Award className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 dark:text-gray-300">{member.expertise_area}</span>
                </div>
              )}

              {/* Affiliation */}
              {member.affiliation && (
                <div className="flex items-start gap-2 text-sm">
                  <Building2 className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 dark:text-gray-300">{member.affiliation}</span>
                </div>
              )}

              {/* Contact Info */}
              <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                {member.email && (
                  <a
                    href={`mailto:${member.email}`}
                    className="flex items-center gap-2 text-sm text-brand-blue hover:text-brand-blue-light"
                  >
                    <Mail className="w-4 h-4" />
                    <span className="truncate">{member.email}</span>
                  </a>
                )}
                {member.phone && (
                  <a
                    href={`tel:${member.phone}`}
                    className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-brand-blue"
                  >
                    <Phone className="w-4 h-4" />
                    {member.phone}
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* No Results */}
      {filteredMembers.length === 0 && (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <Users className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No members found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Try adjusting your search or filters
          </p>
        </div>
      )}
    </div>
  );
};

export default SSCMembers;
