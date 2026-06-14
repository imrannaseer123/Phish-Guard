
const { useState, useEffect, useRef } = React;

const DashboardCharts = ({ summary, weeklyTrend, isLight }) => {
    const dailyChartRef = useRef(null);
    const intentChartRef = useRef(null);
    const brandChartRef = useRef(null);
    const intentTrendChartRef = useRef(null);
    const trendChartRef = useRef(null);
    const charts = useRef({});

    const gridColor = isLight ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.08)';
    const labelColor = isLight ? '#475569' : '#94a3b8';
    const fontFamily = "'Inter', sans-serif";

    // Helper to destroy old charts
    const destroyChart = (key) => {
        if (charts.current[key]) {
            charts.current[key].destroy();
        }
    };

    /**
     * 1. Daily Activity Chart
     */
    useEffect(() => {
        if (!summary || !dailyChartRef.current) return;
        destroyChart('daily');

        const ctx = dailyChartRef.current.getContext('2d');
        charts.current['daily'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: summary.daily_labels,
                datasets: [
                    {
                        label: 'Total Scanned',
                        data: summary.daily_scan_values,
                        backgroundColor: 'rgba(99, 102, 241, 0.6)',
                        borderColor: '#6366f1',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Risky (Med+High)',
                        data: summary.daily_risk_values,
                        backgroundColor: 'rgba(239, 68, 68, 0.6)',
                        borderColor: '#ef4444',
                        borderWidth: 1,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: labelColor, font: { family: fontFamily } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: gridColor },
                        ticks: { color: labelColor, stepSize: 1, font: { family: fontFamily } }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: labelColor, font: { family: fontFamily }, usePointStyle: true }
                    }
                }
            }
        });

        return () => destroyChart('daily');
    }, [summary, isLight]);

    /**
     * 2. Intent Distribution Chart
     */
    useEffect(() => {
        if (!summary || !summary.intent_distribution || !intentChartRef.current) return;
        destroyChart('intent');

        const intentLabels = Object.keys(summary.intent_distribution);
        const intentValues = Object.values(summary.intent_distribution);
        const intentColors = intentLabels.map(label => {
            switch (label) {
                case 'Credential Harvesting': return '#ef4444';
                case 'Financial Fraud': return '#f59e0b';
                case 'Malware Delivery': return '#8b5cf6';
                case 'Identity Theft': return '#ec4899';
                case 'Legitimate': return '#22c55e';
                default: return '#6366f1';
            }
        });

        const ctx = intentChartRef.current.getContext('2d');
        charts.current['intent'] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: intentLabels,
                datasets: [{
                    data: intentValues,
                    backgroundColor: intentColors,
                    borderWidth: 0,
                    hoverOffset: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: labelColor,
                            font: { family: fontFamily },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 16,
                        }
                    }
                }
            }
        });

        return () => destroyChart('intent');
    }, [summary, isLight]);

    /**
     * 3. Brand Frequency Chart (Horizontal Bar)
     */
    useEffect(() => {
        if (!summary || !summary.top_brands || !brandChartRef.current) return;
        destroyChart('brand');

        const brandLabels = summary.top_brands.map(b => b[0]);
        const brandCounts = summary.top_brands.map(b => b[1]);

        const ctx = brandChartRef.current.getContext('2d');
        charts.current['brand'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: brandLabels,
                datasets: [{
                    label: 'Impersonation Attempts',
                    data: brandCounts,
                    backgroundColor: 'rgba(245, 158, 11, 0.6)',
                    borderColor: '#f59e0b',
                    borderWidth: 1,
                    borderRadius: 4,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: labelColor, stepSize: 1, font: { family: fontFamily } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: labelColor, font: { family: fontFamily, weight: '500' } }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

        return () => destroyChart('brand');
    }, [summary, isLight]);

    /**
     * 4. Daily Intent Trend Chart (Stacked Bar)
     */
    useEffect(() => {
        if (!summary || !summary.daily_intent_data || !intentTrendChartRef.current) return;
        destroyChart('intentTrend');

        const data = summary.daily_intent_data;
        const datasets = data.intents.map((intent, idx) => {
             const colors = ['#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#22c55e', '#3b82f6'];
             const color = colors[idx % colors.length];
             return {
                 label: intent,
                 data: data.series[intent],
                 backgroundColor: color,
                 stack: 'Stack 0',
             };
        });

        const ctx = intentTrendChartRef.current.getContext('2d');
        charts.current['intentTrend'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        grid: { color: gridColor },
                        ticks: { color: labelColor, font: { family: fontFamily } }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: { color: gridColor },
                        ticks: { color: labelColor, stepSize: 1, font: { family: fontFamily } }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: labelColor, font: { family: fontFamily }, usePointStyle: true }
                    }
                }
            }
        });

        return () => destroyChart('intentTrend');
    }, [summary, isLight]);

    /**
     * 3. Risk Trend Chart
     */
    useEffect(() => {
        if (!weeklyTrend || weeklyTrend.length === 0 || !trendChartRef.current) return;
        destroyChart('trend');

        const trendLabels = weeklyTrend.map(t => t.date);
        const trendScores = weeklyTrend.map(t => t.score);

        const ctx = trendChartRef.current.getContext('2d');
        charts.current['trend'] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    label: 'Risk Score',
                    data: trendScores,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#8b5cf6',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: labelColor, maxTicksLimit: 10, font: { family: fontFamily } }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: gridColor },
                        ticks: { color: labelColor, font: { family: fontFamily } }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return 'Risk Score: ' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });

        return () => destroyChart('trend');
    }, [weeklyTrend, isLight]);

    return (
        <React.Fragment>
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Daily Scan Chart */}
                <div className="bg-white dark:bg-slate-800/60 backdrop-blur-md rounded-xl p-6 border border-slate-200 dark:border-white/10 shadow-sm flex flex-col">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">📊 Daily Activity</h2>
                    <div className="relative w-full h-64 md:h-80">
                        <canvas ref={dailyChartRef}></canvas>
                    </div>
                </div>

                {/* Intent Distribution Chart */}
                <div className="bg-white dark:bg-slate-800/60 backdrop-blur-md rounded-xl p-6 border border-slate-200 dark:border-white/10 shadow-sm flex flex-col">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">🎯 Intent Distribution</h2>
                    <div className="relative w-full h-64 md:h-80 flex items-center justify-center">
                        <canvas ref={intentChartRef}></canvas>
                    </div>
                </div>
            </div>

            {/* Row 2: Brand Frequency & Intent Trends */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Brand Frequency */}
                <div className="bg-white dark:bg-slate-800/60 backdrop-blur-md rounded-xl p-6 border border-slate-200 dark:border-white/10 shadow-sm flex flex-col">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">🏢 Top Targeted Brands</h2>
                    <div className="relative w-full h-64 md:h-80">
                        <canvas ref={brandChartRef}></canvas>
                    </div>
                </div>

                {/* Intent Trend */}
                <div className="bg-white dark:bg-slate-800/60 backdrop-blur-md rounded-xl p-6 border border-slate-200 dark:border-white/10 shadow-sm flex flex-col">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">📈 Phishing Intent Trends</h2>
                    <div className="relative w-full h-64 md:h-80">
                        <canvas ref={intentTrendChartRef}></canvas>
                    </div>
                </div>
            </div>

            {/* Risk Trend Chart */}
            {weeklyTrend && weeklyTrend.length > 0 && (
                <div className="bg-white dark:bg-slate-800/60 backdrop-blur-md rounded-xl p-6 border border-slate-200 dark:border-white/10 shadow-sm flex flex-col mb-6">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">📉 Risk Score Trend (Last 20 Scans)</h2>
                    <div className="relative w-full h-64 md:h-80">
                        <canvas ref={trendChartRef}></canvas>
                    </div>
                </div>
            )}
        </React.Fragment>
    );
};

// Mount Logic
const mountNode = document.getElementById('react-dashboard-root');
if (mountNode) {
    const root = ReactDOM.createRoot(mountNode);
    // Parse data from global variables injected by Jinja
    const summaryData = window.DASHBOARD_SUMMARY || {};
    const trendData = window.WEEKLY_TREND || [];
    const isLightMode = document.documentElement.getAttribute('data-theme') === 'light';

    root.render(
        <DashboardCharts
            summary={summaryData}
            weeklyTrend={trendData}
            isLight={isLightMode}
        />
    );
}
