// Dashboard JavaScript - Modularizado
// Arquivo: meu_app/static/dashboard.js

class DashboardManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupThermometer();
        this.setupDrillDown();
        this.setupCharts();
    }

    // Termômetro Simplificado
    setupThermometer() {
        const margemManobra = window.margemManobra || 0;
        const indicator = document.getElementById('thermometer-indicator');
        
        if (!indicator) return;

        // Calcular posição baseada na margem
        let position = 50; // Neutro (50%)
        
        if (margemManobra <= -3000) {
            position = 10; // Crítico
        } else if (margemManobra <= 0) {
            position = 30; // Alerta
        } else if (margemManobra <= 2000) {
            position = 70; // Bom
        } else {
            position = 90; // Excelente
        }

        indicator.style.left = position + '%';
    }

    // Drill-down nos KPIs
    setupDrillDown() {
        window.showDrillDown = (kpiType) => {
            this.showDrillDown(kpiType);
        };
    }

    showDrillDown(kpiType) {
        const messages = {
            'faturamento': 'Redirecionando para relatório de faturamento...',
            'verbas': 'Redirecionando para detalhamento de verbas...',
            'cpv': 'Redirecionando para análise de custos...',
            'margem': 'Redirecionando para análise de margem...'
        };

        // Por enquanto, apenas mostra uma notificação
        // TODO: Implementar navegação real para relatórios detalhados
        this.showNotification(messages[kpiType] || 'Funcionalidade em desenvolvimento', 'info');
    }

    // Configuração dos gráficos
    setupCharts() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js não carregado');
            return;
        }

        this.setupEvolucaoChart();
    }

    setupEvolucaoChart() {
        const ctx = document.getElementById('evolucaoChart');
        if (!ctx) return;

        const dadosEvolucao = window.dadosEvolucao || {};
        
        new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: dadosEvolucao.labels || [],
                datasets: [
                    {
                        label: 'Receita + Verbas',
                        data: dadosEvolucao.receita_verbas || [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'CPV Total',
                        data: dadosEvolucao.cpv_total || [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Margem',
                        data: dadosEvolucao.margem || [],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    // Sistema de notificações
    showNotification(message, type = 'info') {
        // Usar o sistema de notificações existente se disponível
        if (window.notificationSystem) {
            window.notificationSystem[type](message);
        } else {
            // Fallback simples
            alert(message);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    new DashboardManager();
});

// Exportar para uso global se necessário
window.DashboardManager = DashboardManager;
