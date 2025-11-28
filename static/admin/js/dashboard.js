// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initRevenueChart();
    initCategoryChart();
    
    // Animate numbers on load
    animateNumbers();
    
    console.log('✅ Dashboard loaded successfully');
});

// Revenue Chart
function initRevenueChart() {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Get data from data attribute or use default
    let chartData = {
        labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
        values: [0, 0, 0, 0, 0, 0, 0]
    };
    
    const dataAttr = canvas.getAttribute('data-chart-data');
    if (dataAttr) {
        try {
            chartData = JSON.parse(dataAttr);
        } catch (e) {
            console.error('Error parsing chart data:', e);
        }
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Doanh thu (₫)',
                data: chartData.values,
                borderColor: '#4a9eff',
                backgroundColor: 'rgba(74, 158, 255, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#4a9eff',
                pointBorderColor: '#1a1a1a',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#252525',
                    titleColor: '#e0e0e0',
                    bodyColor: '#e0e0e0',
                    borderColor: '#444',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return new Intl.NumberFormat('vi-VN').format(context.parsed.y) + ' ₫';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#333',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#aaa',
                        callback: function(value) {
                            return new Intl.NumberFormat('vi-VN', {
                                notation: 'compact',
                                compactDisplay: 'short'
                            }).format(value) + ' ₫';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#aaa'
                    }
                }
            }
        }
    });
}

// Category Chart
function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Get data from data attribute or use default
    let chartData = {
        labels: ['Laptop', 'PC', 'Linh kiện', 'Phụ kiện'],
        values: [0, 0, 0, 0]
    };
    
    const dataAttr = canvas.getAttribute('data-chart-data');
    if (dataAttr) {
        try {
            chartData = JSON.parse(dataAttr);
        } catch (e) {
            console.error('Error parsing chart data:', e);
        }
    }
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: [
                    '#4a9eff',
                    '#5cb85c',
                    '#ffc107',
                    '#4285f4'
                ],
                borderColor: '#1a1a1a',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e0e0e0',
                        padding: 16,
                        font: {
                            size: 13
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#252525',
                    titleColor: '#e0e0e0',
                    bodyColor: '#e0e0e0',
                    borderColor: '#444',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Animate numbers
function animateNumbers() {
    const numbers = document.querySelectorAll('.stat-value');
    
    numbers.forEach(element => {
        const target = parseInt(element.textContent.replace(/[^0-9]/g, ''));
        if (isNaN(target)) return;
        
        const duration = 1000;
        const steps = 50;
        const increment = target / steps;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString('vi-VN');
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString('vi-VN');
            }
        }, duration / steps);
    });
}

// Update chart period
function updateChart(period) {
    console.log('Updating chart for period:', period);
    // This would typically make an AJAX request to get new data
    // For now, just reload the page with the period parameter
    const url = new URL(window.location);
    url.searchParams.set('period', period);
    window.location.href = url.toString();
}
