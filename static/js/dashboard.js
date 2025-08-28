/**
 * Kenya-Agor Dashboard JavaScript
 * Handles dashboard interactions, charts, and data visualization
 */

class KenyaAgorDashboard {
    constructor() {
        this.charts = {};
        this.dataUpdateInterval = null;
        this.init();
    }

    init() {
        console.log('Initializing Kenya-Agor Dashboard...');
        this.bindEvents();
        this.initializeTooltips();
        this.setupAutoRefresh();
        this.animateCards();
    }

    bindEvents() {

        // Metric card clicks for detailed view
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.btn')) {
                    this.showMetricDetail(card);
                }
            });
        });

        // Chart type toggle (if needed)
        document.querySelectorAll('[data-chart-type]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chartType = e.target.getAttribute('data-chart-type');
                this.updateChartType(chartType);
            });
        });

        // Responsive chart resize
        window.addEventListener('resize', () => {
            this.resizeCharts();
        });
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Add tooltips to metric cards
        document.querySelectorAll('.metric-card').forEach(card => {
            if (!card.hasAttribute('title')) {
                const title = card.querySelector('h6').textContent;
                card.setAttribute('title', `Click to view ${title} details`);
                card.setAttribute('data-bs-toggle', 'tooltip');
                new bootstrap.Tooltip(card);
            }
        });
    }

    setupAutoRefresh() {
        // Auto-refresh data every 30 minutes
        this.dataUpdateInterval = setInterval(() => {
            this.updateDashboardData(true); // Silent update
        }, 30 * 60 * 1000);

        // Clear interval on page unload
        window.addEventListener('beforeunload', () => {
            if (this.dataUpdateInterval) {
                clearInterval(this.dataUpdateInterval);
            }
        });
    }

    animateCards() {
        // Animate metric cards on page load
        const cards = document.querySelectorAll('.metric-card, .insight-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    async updateDashboardData(silent = false) {
        try {
            if (!silent) {
                this.showLoading('Updating agricultural data...');
            }

            const response = await fetch('/api/update-data', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (result.success) {
                if (!silent) {
                    this.hideLoading();
                    this.showAlert('success', 
                        `Data updated successfully! ${result.records_updated} records updated.`
                    );
                    // Refresh page after a delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    console.log('Dashboard data updated silently:', result);
                }
            } else {
                throw new Error(result.message || 'Failed to update data');
            }

        } catch (error) {
            console.error('Error updating dashboard data:', error);
            if (!silent) {
                this.hideLoading();
                this.showAlert('danger', 
                    'Failed to update data. Please check your connection and try again.'
                );
            }
        }
    }

    exportDashboardData() {
        try {
            // Collect dashboard data
            const dashboardData = {
                timestamp: new Date().toISOString(),
                farmer_profile: this.getFarmerProfile(),
                metrics: this.getMetrics(),
                chart_data: this.getChartData(),
                recommendations: this.getRecommendations(),
                market_data: this.getMarketData()
            };

            // Create and download file
            const dataStr = JSON.stringify(dashboardData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);

            const link = document.createElement('a');
            link.href = url;
            link.download = `kenya-agor-dashboard-${new Date().toISOString().split('T')[0]}.json`;
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(url);

            this.showAlert('success', 'Dashboard data exported successfully!');

        } catch (error) {
            console.error('Error exporting dashboard data:', error);
            this.showAlert('danger', 'Failed to export data. Please try again.');
        }
    }

    getFarmerProfile() {
        const profileElements = {
            name: document.querySelector('h1.h2')?.textContent?.replace('Welcome back, ', '').replace('!', ''),
            location: document.querySelector('.text-muted')?.textContent?.trim()
        };
        return profileElements;
    }

    getMetrics() {
        const metrics = {};
        document.querySelectorAll('.metric-card').forEach((card, index) => {
            const title = card.querySelector('h6')?.textContent?.trim();
            const value = card.querySelector('h4')?.textContent?.trim();
            const description = card.querySelector('small')?.textContent?.trim();
            
            if (title && value) {
                metrics[title] = {
                    value: value,
                    description: description || ''
                };
            }
        });
        return metrics;
    }

    getChartData() {
        // Extract data from existing charts
        const chartData = {};
        Object.keys(this.charts).forEach(chartId => {
            const chart = this.charts[chartId];
            if (chart && chart.data) {
                chartData[chartId] = {
                    labels: chart.data.labels,
                    datasets: chart.data.datasets.map(dataset => ({
                        label: dataset.label,
                        data: dataset.data,
                        backgroundColor: dataset.backgroundColor,
                        borderColor: dataset.borderColor
                    }))
                };
            }
        });
        return chartData;
    }

    getRecommendations() {
        const recommendations = [];
        document.querySelectorAll('.insight-card').forEach(card => {
            const crop = card.querySelector('h6')?.textContent?.trim();
            const reason = card.querySelector('p')?.textContent?.trim();
            const potential = card.querySelector('.badge')?.textContent?.trim();
            
            if (crop && reason) {
                recommendations.push({
                    crop: crop,
                    reason: reason,
                    potential: potential || ''
                });
            }
        });
        return recommendations;
    }

    getMarketData() {
        const marketData = {};
        // Extract market price data from the dashboard
        document.querySelectorAll('.bg-light.rounded').forEach(item => {
            const crop = item.querySelector('.fw-bold')?.textContent?.trim();
            const price = item.querySelector('.fw-bold:last-child')?.textContent?.trim();
            
            if (crop && price && crop !== price) {
                marketData[crop] = price;
            }
        });
        return marketData;
    }

    showMetricDetail(card) {
        const title = card.querySelector('h6').textContent.trim();
        const value = card.querySelector('h4').textContent.trim();
        const description = card.querySelector('small')?.textContent?.trim() || '';

        // Create modal content
        const modalContent = `
            <div class="modal fade" id="metricDetailModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-chart-bar me-2 text-agricultural-green"></i>
                                ${title} Details
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center mb-4">
                                <h2 class="display-4 text-agricultural-green">${value}</h2>
                                <p class="text-muted">${description}</p>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Trend Analysis</h6>
                                    <p class="text-muted">Based on recent data patterns, this metric shows positive growth.</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Recommendations</h6>
                                    <p class="text-muted">Continue monitoring this metric for optimal farming decisions.</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-agricultural-green" onclick="dashboard.exportMetric('${title}')">
                                Export Data
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('metricDetailModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalContent);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('metricDetailModal'));
        modal.show();
    }

    exportMetric(metricTitle) {
        const metricData = {
            title: metricTitle,
            timestamp: new Date().toISOString(),
            data: this.getMetrics()[metricTitle] || {}
        };

        const dataStr = JSON.stringify(metricData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);

        const link = document.createElement('a');
        link.href = url;
        link.download = `${metricTitle.toLowerCase().replace(/\s+/g, '-')}-data.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        
        this.showAlert('success', `${metricTitle} data exported successfully!`);
    }

    updateChartType(chartType) {
        const chart = this.charts.productionChart;
        if (chart) {
            chart.config.type = chartType;
            chart.update();
            
            this.showAlert('info', `Chart updated to ${chartType} view`);
        }
    }

    resizeCharts() {
        // Resize all charts when window is resized
        Object.keys(this.charts).forEach(chartId => {
            const chart = this.charts[chartId];
            if (chart) {
                chart.resize();
            }
        });
    }

    showLoading(message = 'Loading...') {
        // Remove existing loading modal
        const existingModal = document.getElementById('dynamicLoadingModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create loading modal
        const modalHTML = `
            <div class="modal fade" id="dynamicLoadingModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered modal-sm">
                    <div class="modal-content">
                        <div class="modal-body text-center p-4">
                            <div class="spinner-border text-agricultural-green mb-3" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <h6 class="mb-0">${message}</h6>
                            <small class="text-muted">Please wait...</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('dynamicLoadingModal'));
        modal.show();
    }

    hideLoading() {
        const modal = document.getElementById('dynamicLoadingModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
            setTimeout(() => modal.remove(), 300);
        }
    }

    showAlert(type, message, duration = 5000) {
        const alertId = `alert-${Date.now()}`;
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
                 id="${alertId}"
                 style="top: 100px; right: 20px; z-index: 9999; min-width: 300px;">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', alertHTML);

        // Auto-remove after duration
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert && alert.parentNode) {
                alert.remove();
            }
        }, duration);
    }

    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Add chart to registry
    registerChart(id, chart) {
        this.charts[id] = chart;
        console.log(`Chart '${id}' registered successfully`);
    }

    // Get chart by ID
    getChart(id) {
        return this.charts[id];
    }

    // Destroy chart
    destroyChart(id) {
        if (this.charts[id]) {
            this.charts[id].destroy();
            delete this.charts[id];
            console.log(`Chart '${id}' destroyed`);
        }
    }

    // Utility method for formatting numbers
    formatNumber(num, decimals = 0) {
        if (num === null || num === undefined) return 'N/A';
        return Number(num).toLocaleString('en-KE', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    // Utility method for formatting currency
    formatCurrency(amount, currency = 'KES') {
        if (amount === null || amount === undefined) return 'N/A';
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    // Clean up on page unload
    destroy() {
        if (this.dataUpdateInterval) {
            clearInterval(this.dataUpdateInterval);
        }
        
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
        
        console.log('Kenya-Agor Dashboard destroyed');
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', function() {
    dashboard = new KenyaAgorDashboard();
    
    // Make dashboard available globally for onclick handlers
    window.dashboard = dashboard;
    
    // Global functions for backward compatibility
    window.updateData = function() {
        // Show loading state
        const updateBtn = event.target;
        const originalText = updateBtn.innerHTML;
        updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';
        updateBtn.disabled = true;
        
        fetch('/api/update-data')
            .then(response => response.json())
            .then(data => {
                updateBtn.innerHTML = originalText;
                updateBtn.disabled = false;
                
                if (data.success) {
                    dashboard.showAlert('success', `${data.message} at ${new Date(data.timestamp).toLocaleString()}`);
                    
                    if (data.latest_data && data.latest_data.length > 0) {
                        showLatestDataModal(data.latest_data);
                    }
                    
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    alert('Failed to update data: ' + data.message);
                }
            })
            .catch(error => {
                updateBtn.innerHTML = originalText;
                updateBtn.disabled = false;
                alert('Error updating data: ' + error.message);
            });
    };
    
    window.viewExtractedData = function() {
        fetch('/api/data/view')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showDataViewerModal(data.data, data.pagination);
                } else {
                    alert('Failed to load data: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error loading data: ' + error.message);
            });
    };
    
    window.exportData = () => dashboard.exportDashboardData();
    
    // Helper functions for modals
    function showLatestDataModal(latestData) {
        let modal = document.getElementById('latestDataModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'latestDataModal';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Latest Data Fetched</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Crop</th>
                                            <th>County</th>
                                            <th>Value</th>
                                            <th>Unit</th>
                                            <th>Year</th>
                                            <th>Source</th>
                                        </tr>
                                    </thead>
                                    <tbody id="latest-data-tbody">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        const tbody = document.getElementById('latest-data-tbody');
        tbody.innerHTML = latestData.map(item => `
            <tr>
                <td>${item.crop || 'N/A'}</td>
                <td>${item.county || 'N/A'}</td>
                <td>${item.value || 'N/A'}</td>
                <td>${item.unit || 'N/A'}</td>
                <td>${item.year || 'N/A'}</td>
                <td><span class="badge bg-primary">${item.source}</span></td>
            </tr>
        `).join('');
        
        const modalElement = document.getElementById('latestDataModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();
    }
    
    function showDataViewerModal(data, pagination) {
        let modal = document.getElementById('dataViewerModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'dataViewerModal';
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Agricultural Data Viewer</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div id="data-viewer-content"></div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        const content = document.getElementById('data-viewer-content');
        content.innerHTML = `
            <div class="mb-3">
                <strong>Total Records:</strong> ${pagination.total} | 
                <strong>Page:</strong> ${pagination.page} of ${pagination.pages}
            </div>
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Source</th>
                            <th>Crop</th>
                            <th>County</th>
                            <th>Value</th>
                            <th>Unit</th>
                            <th>Year</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(item => `
                            <tr>
                                <td>${item.id}</td>
                                <td><span class="badge bg-primary">${item.source}</span></td>
                                <td>${item.crop || 'N/A'}</td>
                                <td>${item.county || 'N/A'}</td>
                                <td>${item.value || 'N/A'}</td>
                                <td>${item.unit || 'N/A'}</td>
                                <td>${item.year || 'N/A'}</td>
                                <td>${new Date(item.created_at).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        const modalElement = document.getElementById('dataViewerModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();
    }
});

// Clean up when page unloads
window.addEventListener('beforeunload', function() {
    if (dashboard) {
        dashboard.destroy();
    }
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KenyaAgorDashboard;
}
