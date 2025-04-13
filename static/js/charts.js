/**
 * Charts.js for Blood Donation Management System
 * This file contains chart creation and configuration functions
 */

// Function to create blood inventory pie chart
function createBloodInventoryChart(elementId, data) {
    if (!document.getElementById(elementId)) return;

    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default data if no data is provided
    const chartData = data || {
        labels: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        data: [0, 0, 0, 0, 0, 0, 0, 0]
    };
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: [
                    '#dc3545', // A+
                    '#e35d6a', // A-
                    '#0d6efd', // B+
                    '#4d94ff', // B-
                    '#6610f2', // AB+
                    '#8540f5', // AB-
                    '#20c997', // O+
                    '#5dd6b4'  // O-
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} units (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Function to create donations time series chart
function createDonationsTimeChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default data if no data is provided
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = new Date().getMonth();
    
    const labels = [];
    for (let i = 11; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12;
        labels.push(monthNames[monthIndex]);
    }
    
    const chartData = data || {
        labels: labels,
        data: Array(12).fill(0)
    };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Donations per Month',
                data: chartData.data,
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderColor: '#0d6efd',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Donations'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            }
        }
    });
}

// Function to create blood groups bar chart
function createBloodGroupsChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default data if no data is provided
    const chartData = data || {
        labels: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        data: [0, 0, 0, 0, 0, 0, 0, 0]
    };
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Donations by Blood Group',
                data: chartData.data,
                backgroundColor: 'rgba(220, 53, 69, 0.7)',
                borderColor: '#dc3545',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Donations'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Blood Group'
                    }
                }
            }
        }
    });
}

// Function to create a comparison chart for fulfilled vs pending requests
function createRequestsComparisonChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default data if no data is provided
    const chartData = data || {
        labels: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        fulfilled: [0, 0, 0, 0, 0, 0, 0, 0],
        pending: [0, 0, 0, 0, 0, 0, 0, 0]
    };
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Fulfilled Requests',
                    data: chartData.fulfilled,
                    backgroundColor: 'rgba(25, 135, 84, 0.7)',
                    borderColor: '#198754',
                    borderWidth: 1
                },
                {
                    label: 'Pending Requests',
                    data: chartData.pending,
                    backgroundColor: 'rgba(255, 193, 7, 0.7)',
                    borderColor: '#ffc107',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: false,
                    title: {
                        display: true,
                        text: 'Blood Group'
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Requests'
                    }
                }
            }
        }
    });
}

// Function to create a donut chart for request priorities
function createRequestPriorityChart(elementId, data) {
    if (!document.getElementById(elementId)) return;
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default data if no data is provided
    const chartData = data || {
        labels: ['Critical', 'High', 'Medium', 'Low'],
        data: [0, 0, 0, 0]
    };
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: [
                    '#dc3545', // Critical
                    '#ffc107', // High
                    '#0d6efd', // Medium
                    '#6c757d'  // Low
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        padding: 10
                    }
                }
            }
        }
    });
}

// Initialize charts when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we have chart data in the page (populated by Django template)
    const bloodDataJson = document.getElementById('blood-data-json');
    const timeSeriesDataJson = document.getElementById('time-series-data-json');
    const bloodGroupDataJson = document.getElementById('blood-group-data-json');
    
    // Parse the data if available
    let bloodData = null;
    let timeSeriesData = null;
    let bloodGroupData = null;
    
    if (bloodDataJson) {
        try {
            bloodData = JSON.parse(bloodDataJson.textContent);
        } catch (e) {
            console.error('Error parsing blood data JSON:', e);
        }
    }
    
    if (timeSeriesDataJson) {
        try {
            timeSeriesData = JSON.parse(timeSeriesDataJson.textContent);
        } catch (e) {
            console.error('Error parsing time series data JSON:', e);
        }
    }
    
    if (bloodGroupDataJson) {
        try {
            bloodGroupData = JSON.parse(bloodGroupDataJson.textContent);
        } catch (e) {
            console.error('Error parsing blood group data JSON:', e);
        }
    }
    
    // Create charts with the data
    createBloodInventoryChart('bloodInventoryChart', bloodData);
    createDonationsTimeChart('donationsTimeChart', timeSeriesData);
    createBloodGroupsChart('bloodGroupsChart', bloodGroupData);
    
    // These charts may not be present on all pages
    createRequestsComparisonChart('requestsComparisonChart');
    createRequestPriorityChart('requestPriorityChart');
});
