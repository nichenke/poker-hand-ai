// GTO Analysis Visualizer Scripts

document.addEventListener('DOMContentLoaded', function () {
    // Initialize theme
    initTheme();

    // Table sorting functionality
    initTableSorting();

    // AI trigger functionality
    initAITriggers();

    // Modal functionality
    initModal();
});

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;
    const themeIcon = document.querySelector('.theme-icon');

    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme, themeIcon);
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    const themeIcon = document.querySelector('.theme-icon');

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme, themeIcon);

    // Add a smooth transition effect
    document.body.style.transition = 'all 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

function updateThemeIcon(theme, iconElement) {
    if (iconElement) {
        iconElement.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

function initTableSorting() {
    const table = document.getElementById('gtoTable');
    if (!table) return;

    const headers = table.querySelectorAll('th[data-sort]');

    headers.forEach(header => {
        header.addEventListener('click', function () {
            const sortKey = this.dataset.sort;
            const isCurrentlySorted = this.classList.contains('sorted');
            const isDesc = this.classList.contains('desc');

            // Remove sorting from all headers
            headers.forEach(h => h.classList.remove('sorted', 'desc'));

            // Add sorting to clicked header
            this.classList.add('sorted');
            if (isCurrentlySorted && !isDesc) {
                this.classList.add('desc');
            }

            sortTable(table, sortKey, isCurrentlySorted && !isDesc);
        });
    });
}

function sortTable(table, sortKey, descending = false) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        let aVal, bVal;

        switch (sortKey) {
            case 'hand_id':
                aVal = a.querySelector('.hand-id a').textContent.replace('#', '');
                bVal = b.querySelector('.hand-id a').textContent.replace('#', '');
                return descending ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);

            case 'hole_cards':
                aVal = a.querySelector('.cards-display').textContent;
                bVal = b.querySelector('.cards-display').textContent;
                return descending ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);

            case 'position':
                aVal = a.querySelector('.position-badge').textContent;
                bVal = b.querySelector('.position-badge').textContent;
                // Custom position order
                const posOrder = ['BB', 'SB', 'BTN', 'CO', 'MP', 'MP1', 'UTG1', 'UTG', 'HJ'];
                const aPosIndex = posOrder.indexOf(aVal);
                const bPosIndex = posOrder.indexOf(bVal);
                return descending ? bPosIndex - aPosIndex : aPosIndex - bPosIndex;

            case 'stakes':
                aVal = a.querySelector('.stakes-badge').textContent;
                bVal = b.querySelector('.stakes-badge').textContent;
                return descending ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);

            case 'game_type':
                aVal = a.querySelector('.game-type') ? a.querySelector('.game-type').textContent : '';
                bVal = b.querySelector('.game-type') ? b.querySelector('.game-type').textContent : '';
                return descending ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);

            case 'deviation_score':
                aVal = parseFloat(a.querySelector('.deviation-badge').textContent);
                bVal = parseFloat(b.querySelector('.deviation-badge').textContent);
                return descending ? bVal - aVal : aVal - bVal;

            case 'total_ev':
                aVal = parseFloat(a.querySelector('.ev-value').textContent);
                bVal = parseFloat(b.querySelector('.ev-value').textContent);
                return descending ? bVal - aVal : aVal - bVal;

            case 'max_frequency':
                aVal = parseFloat(a.querySelector('.max-frequency').textContent);
                bVal = parseFloat(b.querySelector('.max-frequency').textContent);
                return descending ? bVal - aVal : aVal - bVal;

            case 'processing_time':
                aVal = parseFloat(a.querySelector('.processing-time').textContent);
                bVal = parseFloat(b.querySelector('.processing-time').textContent);
                return descending ? bVal - aVal : aVal - bVal;

            case 'processed_at':
                aVal = new Date(a.querySelector('.processed-at').textContent);
                bVal = new Date(b.querySelector('.processed-at').textContent);
                return descending ? bVal - aVal : aVal - bVal;

            default:
                return 0;
        }
    });

    // Remove existing rows and add sorted rows
    rows.forEach(row => tbody.removeChild(row));
    rows.forEach(row => tbody.appendChild(row));
}

function initAITriggers() {
    const triggerButtons = document.querySelectorAll('.trigger-ai');
    const viewButtons = document.querySelectorAll('.view-ai');

    triggerButtons.forEach(button => {
        button.addEventListener('click', function () {
            const handId = this.dataset.handId;
            const deviation = this.dataset.deviation;

            triggerAIAnalysis(handId, deviation, this);
        });
    });

    viewButtons.forEach(button => {
        button.addEventListener('click', function () {
            const handId = this.dataset.handId;

            // Find and navigate to the analysis file
            fetch(`/api/find_analysis/${handId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.found) {
                        window.location.href = data.url;
                    } else {
                        showNotification('❌ Analysis file not found', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error finding analysis:', error);
                    showNotification('❌ Error finding analysis file', 'error');
                });
        });
    });
}

function triggerAIAnalysis(handId, deviation, button) {
    // Disable button and show loading
    button.disabled = true;
    button.textContent = '🔄 Starting...';

    // Show status
    const statusDiv = document.getElementById(`status-${handId}`);
    if (statusDiv) {
        statusDiv.style.display = 'block';
    }

    // Show modal if on main page
    showAIModal(handId, deviation);

    // Make API call to trigger AI analysis
    fetch(`/api/trigger_ai/${handId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                button.textContent = '🔄 Running...';

                // Start polling for completion
                pollAIStatus(handId, button);
            } else {
                throw new Error(data.error || 'Failed to start AI analysis');
            }
        })
        .catch(error => {
            console.error('Error triggering AI analysis:', error);
            button.disabled = false;
            button.textContent = '❌ Error - Retry';

            if (statusDiv) {
                statusDiv.innerHTML = '<span style="color: red;">❌ Error starting analysis</span>';
            }

            hideAIModal();
        });
}

function pollAIStatus(handId, button) {
    const pollInterval = setInterval(() => {
        fetch(`/api/check_ai_status/${handId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'complete') {
                    clearInterval(pollInterval);

                    // Update button to success state
                    button.textContent = '✅ View AI Analysis';
                    button.disabled = false;
                    button.onclick = () => window.location.href = data.url;
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-success');

                    // Hide status and modal
                    const statusDiv = document.getElementById(`status-${handId}`);
                    if (statusDiv) {
                        statusDiv.style.display = 'none';
                    }

                    hideAIModal();

                    // Show success message
                    showNotification('✅ AI Analysis Complete!', 'success');

                } else if (data.status === 'error') {
                    clearInterval(pollInterval);

                    button.disabled = false;
                    button.textContent = '❌ Error - Retry';

                    hideAIModal();
                    showNotification('❌ AI Analysis Failed', 'error');
                }
                // Continue polling if status is 'pending'
            })
            .catch(error => {
                console.error('Error checking AI status:', error);
                clearInterval(pollInterval);

                button.disabled = false;
                button.textContent = '❌ Error - Retry';

                hideAIModal();
                showNotification('❌ Error checking analysis status', 'error');
            });
    }, 3000); // Poll every 3 seconds
}

function initModal() {
    const modal = document.getElementById('aiModal');
    if (!modal) return;

    const closeBtn = modal.querySelector('.modal-close');

    closeBtn.addEventListener('click', hideAIModal);

    // Close on background click
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            hideAIModal();
        }
    });
}

function showAIModal(handId, deviation) {
    const modal = document.getElementById('aiModal');
    if (!modal) return;

    const handIdSpan = document.getElementById('modalHandId');
    const deviationSpan = document.getElementById('modalDeviation');

    if (handIdSpan) handIdSpan.textContent = handId;
    if (deviationSpan) deviationSpan.textContent = deviation;

    modal.style.display = 'flex';
}

function hideAIModal() {
    const modal = document.getElementById('aiModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">✕</button>
    `;

    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        min-width: 300px;
        max-width: 500px;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        font-weight: 500;
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    `;

    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    } else if (type === 'warning') {
        notification.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)';
    }

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return '✅';
        case 'error': return '❌';
        case 'warning': return '⚠️';
        default: return 'ℹ️';
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
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
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);