let chartSectores = null;
let chartProblemas = null;
let chartTendencia = null;
let chartSriePilares = null;
let chartSrieUrgencia = null;
let chartSrieImpacto = null;
let apiUrls = {};

const COLORS = [
    '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#ec4899', '#f97316', '#6366f1', '#14b8a6',
    '#a855f7', '#0891b2'
];

const URGENCIA_COLORS = {
    'Crítica': '#dc2626',
    'Alta': '#ea580c',
    'Moderada': '#ca8a04',
    'Baja': '#16a34a',
};

const IMPACTO_COLORS = {
    'Nacional': '#7c3aed',
    'Regional': '#2563eb',
    'Local': '#059669',
};

document.addEventListener('DOMContentLoaded', function() {
    apiUrls = {
        estadisticas: document.getElementById('apiEstadisticasUrl')?.value || '/api/estadisticas'
    };
    cargarEstadisticas();
});

async function cargarEstadisticas() {
    try {
        const response = await fetch(apiUrls.estadisticas);
        const data = await response.json();

        document.getElementById('totalParticipaciones').textContent = data.total_participaciones;
        document.getElementById('totalPoliticas').textContent = data.total_politicas || 0;
        document.getElementById('totalDepartamentos').textContent = data.total_departamentos;
        document.getElementById('totalSectores').textContent = data.sectores.length;

        renderChartSectores(data.sectores);
        renderListaDepartamentos(data.departamentos);
        renderChartProblemas(data.problemas);
        renderChartTendencia(data.tendencia);
        renderListaPropuestas(data.propuestas_recientes);
        renderChartSriePilares(data.srie_pilares);
        renderChartSrieUrgencia(data.srie_urgencia);
        renderChartSrieImpacto(data.srie_impacto);

    } catch (error) {
        console.error('Error:', error);
    }
}

function renderChartSectores(sectores) {
    const ctx = document.getElementById('chartSectores')?.getContext('2d');
    if (!ctx) return;
    if (chartSectores) chartSectores.destroy();

    chartSectores = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sectores.map(s => s.nombre),
            datasets: [{
                label: 'Participaciones',
                data: sectores.map(s => s.total),
                backgroundColor: sectores.map((_, i) => COLORS[i % COLORS.length] + 'cc'),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderListaDepartamentos(departamentos) {
    const container = document.getElementById('listaDepartamentos');
    if (!container) return;

    if (departamentos.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay datos disponibles</p>';
        return;
    }

    const maxTotal = Math.max(...departamentos.map(d => d.total));

    let html = '';
    departamentos.forEach((d, i) => {
        const width = (d.total / maxTotal) * 100;
        const color = i < 3 ? COLORS[i] : COLORS[3];
        html += `
            <div class="depto-bar mb-2">
                <div class="d-flex justify-content-between small mb-1">
                    <span class="fw-medium">${d.nombre}</span>
                    <span class="text-muted fw-bold">${d.total}</span>
                </div>
                <div class="progress" style="height: 10px; border-radius: 6px; background: #f1f5f9;">
                    <div class="progress-bar" style="width: ${width}%; background: ${color}; border-radius: 6px; transition: width 1s ease;"></div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function renderChartProblemas(problemas) {
    const ctx = document.getElementById('chartProblemas')?.getContext('2d');
    if (!ctx) return;
    if (chartProblemas) chartProblemas.destroy();

    chartProblemas = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: problemas.map(p => p.nombre),
            datasets: [{
                data: problemas.map(p => p.total),
                backgroundColor: problemas.map((_, i) => COLORS[i % COLORS.length] + 'cc'),
                borderWidth: 2,
                borderColor: 'white',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 12, font: { size: 11 } }
                }
            }
        }
    });
}

function renderChartTendencia(tendencia) {
    const ctx = document.getElementById('chartTendencia')?.getContext('2d');
    if (!ctx) return;
    if (chartTendencia) chartTendencia.destroy();

    chartTendencia = new Chart(ctx, {
        type: 'line',
        data: {
            labels: tendencia.map(t => t.fecha),
            datasets: [{
                label: 'Participaciones',
                data: tendencia.map(t => t.total),
                borderColor: '#2563eb',
                backgroundColor: (ctx) => {
                    const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 300);
                    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.2)');
                    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.0)');
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: 'white',
                pointBorderColor: '#2563eb',
                pointBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderListaPropuestas(propuestas) {
    const container = document.getElementById('listaPropuestas');
    if (!container) return;

    if (propuestas.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay propuestas registradas aún</p>';
        return;
    }

    let html = '<div class="row g-3">';
    propuestas.forEach(p => {
        html += `
            <div class="col-md-6">
                <div class="card h-100 border-0" style="background: #f8fafc; border-radius: 16px;">
                    <div class="card-body">
                        <p class="card-text fst-italic">"${p.propuesta}"</p>
                        <div class="d-flex justify-content-between small text-muted mt-3">
                            <span><i class="bi bi-geo-alt me-1"></i>${p.departamento || 'No especificado'}</span>
                            <span>${p.fecha}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function renderChartSriePilares(pilares) {
    const ctx = document.getElementById('chartSriePilares')?.getContext('2d');
    if (!ctx) return;
    if (chartSriePilares) chartSriePilares.destroy();

    chartSriePilares = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: pilares.map(p => p.nombre),
            datasets: [{
                data: pilares.map(p => p.total),
                backgroundColor: pilares.map((_, i) => COLORS[i % COLORS.length] + 'cc'),
                borderWidth: 2,
                borderColor: 'white',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '50%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 10, font: { size: 10 } }
                }
            }
        }
    });
}

function renderChartSrieUrgencia(urgencia) {
    const ctx = document.getElementById('chartSrieUrgencia')?.getContext('2d');
    if (!ctx) return;
    if (chartSrieUrgencia) chartSrieUrgencia.destroy();

    chartSrieUrgencia = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: urgencia.map(u => u.nombre),
            datasets: [{
                label: 'Participaciones',
                data: urgencia.map(u => u.total),
                backgroundColor: urgencia.map(u => (URGENCIA_COLORS[u.nombre] || '#94a3b8') + 'cc'),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, ticks: { stepSize: 1 } },
                y: { grid: { display: false } }
            }
        }
    });
}

function renderChartSrieImpacto(impacto) {
    const ctx = document.getElementById('chartSrieImpacto')?.getContext('2d');
    if (!ctx) return;
    if (chartSrieImpacto) chartSrieImpacto.destroy();

    chartSrieImpacto = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: impacto.map(i => i.nombre),
            datasets: [{
                label: 'Participaciones',
                data: impacto.map(i => i.total),
                backgroundColor: impacto.map(i => (IMPACTO_COLORS[i.nombre] || '#94a3b8') + 'cc'),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, ticks: { stepSize: 1 } },
                y: { grid: { display: false } }
            }
        }
    });
}
