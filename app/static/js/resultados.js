let chartSectores = null;
let chartProblemas = null;
let chartTendencia = null;
let apiUrls = {};

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
        document.getElementById('totalPropuestas').textContent = data.total_participaciones;
        document.getElementById('totalDepartamentos').textContent = data.total_departamentos;
        document.getElementById('totalSectores').textContent = data.sectores.length;

        renderChartSectores(data.sectores);
        renderListaDepartamentos(data.departamentos);
        renderChartProblemas(data.problemas);
        renderChartTendencia(data.tendencia);
        renderListaPropuestas(data.propuestas_recientes);

    } catch (error) {
        console.error('Error:', error);
    }
}

function renderChartSectores(sectores) {
    const ctx = document.getElementById('chartSectores').getContext('2d');

    if (chartSectores) chartSectores.destroy();

    chartSectores = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sectores.map(s => s.nombre),
            datasets: [{
                label: 'Participaciones',
                data: sectores.map(s => s.total),
                backgroundColor: [
                    'rgba(13, 110, 253, 0.8)',
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(108, 117, 125, 0.8)',
                    'rgba(13, 202, 240, 0.8)',
                    'rgba(111, 66, 193, 0.8)',
                    'rgba(253, 126, 20, 0.8)',
                    'rgba(20, 184, 166, 0.8)',
                    'rgba(219, 39, 119, 0.8)'
                ],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

function renderListaDepartamentos(departamentos) {
    const container = document.getElementById('listaDepartamentos');

    if (departamentos.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay datos disponibles</p>';
        return;
    }

    const maxTotal = Math.max(...departamentos.map(d => d.total));

    let html = '';
    departamentos.forEach(d => {
        const width = (d.total / maxTotal) * 100;
        html += `
            <div class="mb-2">
                <div class="d-flex justify-content-between small">
                    <span>${d.nombre}</span>
                    <span class="text-muted">${d.total}</span>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-primary" style="width: ${width}%"></div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function renderChartProblemas(problemas) {
    const ctx = document.getElementById('chartProblemas').getContext('2d');

    if (chartProblemas) chartProblemas.destroy();

    chartProblemas = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: problemas.map(p => p.nombre),
            datasets: [{
                data: problemas.map(p => p.total),
                backgroundColor: [
                    'rgba(13, 110, 253, 0.8)',
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(108, 117, 125, 0.8)',
                    'rgba(13, 202, 240, 0.8)',
                    'rgba(111, 66, 193, 0.8)',
                    'rgba(253, 126, 20, 0.8)',
                    'rgba(20, 184, 166, 0.8)',
                    'rgba(219, 39, 119, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12 }
                }
            }
        }
    });
}

function renderChartTendencia(tendencia) {
    const ctx = document.getElementById('chartTendencia').getContext('2d');

    if (chartTendencia) chartTendencia.destroy();

    chartTendencia = new Chart(ctx, {
        type: 'line',
        data: {
            labels: tendencia.map(t => t.fecha),
            datasets: [{
                label: 'Participaciones',
                data: tendencia.map(t => t.total),
                borderColor: 'rgba(13, 110, 253, 1)',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

function renderListaPropuestas(propuestas) {
    const container = document.getElementById('listaPropuestas');

    if (propuestas.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay propuestas registradas aún</p>';
        return;
    }

    let html = '<div class="row g-3">';
    propuestas.forEach(p => {
        html += `
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-body">
                        <p class="card-text">"${p.propuesta}"</p>
                        <div class="d-flex justify-content-between small text-muted">
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
