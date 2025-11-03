// SAFMC FMP Tracker - Frontend JavaScript

// API Base URL
const API_BASE = '/api';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

// Load dashboard statistics and recent actions
async function loadDashboardData() {
    try {
        // Load statistics
        const statsResponse = await fetch(`${API_BASE}/dashboard/stats`);
        const stats = await statsResponse.json();

        document.getElementById('total-actions').textContent = stats.totalActions || 0;
        document.getElementById('pending-review').textContent = stats.pendingReview || 0;
        document.getElementById('upcoming-meetings').textContent = stats.upcomingMeetings || 0;
        document.getElementById('recent-comments').textContent = stats.recentComments || 0;

        // Load recent amendments
        const actionsResponse = await fetch(`${API_BASE}/dashboard/recent-amendments?limit=10`);
        const actionsData = await actionsResponse.json();

        displayActions(actionsData.actions);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

// Display actions in table
function displayActions(actions) {
    const tbody = document.getElementById('actions-tbody');

    if (!actions || actions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No actions found</td></tr>';
        return;
    }

    tbody.innerHTML = actions.map(action => `
        <tr>
            <td>
                <strong>${escapeHtml(action.title)}</strong>
                <div style="font-size: 0.9em; color: #6c757d;">${escapeHtml(action.type || '')}</div>
            </td>
            <td>${escapeHtml(action.fmp || 'N/A')}</td>
            <td>
                <span class="badge ${getBadgeClass(action.progressStage)}">
                    ${escapeHtml(action.progressStage || 'N/A')}
                </span>
            </td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${action.progress || 0}%"></div>
                </div>
                <div style="font-size: 0.85em; margin-top: 5px;">${action.progress || 0}%</div>
            </td>
            <td>${formatDate(action.updatedAt)}</td>
        </tr>
    `).join('');
}

// Get badge class based on progress stage
function getBadgeClass(stage) {
    if (!stage) return 'badge-scoping';

    const stageLower = stage.toLowerCase();

    if (stageLower.includes('scoping')) return 'badge-scoping';
    if (stageLower.includes('hearing')) return 'badge-hearing';
    if (stageLower.includes('approval')) return 'badge-approval';
    if (stageLower.includes('implementation')) return 'badge-implementation';

    return 'badge-scoping';
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return 'N/A';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return '';

    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };

    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Trigger manual scrape
async function triggerScrape() {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Updating...';

    try {
        const response = await fetch(`${API_BASE}/scrape/all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            showSuccess('Data updated successfully!');
            // Reload dashboard data
            setTimeout(() => loadDashboardData(), 1000);
        } else {
            showError('Update failed: ' + (result.error || 'Unknown error'));
        }

    } catch (error) {
        console.error('Error triggering scrape:', error);
        showError('Failed to trigger update');
    } finally {
        button.disabled = false;
        button.textContent = 'Update Data';
    }
}

// Show success message
function showSuccess(message) {
    showNotification(message, 'success');
}

// Show error message
function showError(message) {
    showNotification(message, 'error');
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#2ca02c' : '#d62728'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    // Add to page
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
