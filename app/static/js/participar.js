let sectoresSeleccionados = [];
let sectorPrioritarioId = null;
let problemasSeleccionados = {};
let tipoPropuesta = 'unificada';
let apiUrls = {};

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', function() {
    apiUrls = {
        problemas: document.getElementById('apiProblemasUrl')?.value || '/api/problemas/',
        enviar: document.getElementById('apiEnviarUrl')?.value || '/api/enviar',
        confirmacion: document.getElementById('apiConfirmacionUrl')?.value || '/confirmacion'
    };
    initSectorCards();
    initCharCounter();
});

function initSectorCards() {
    document.querySelectorAll('.sector-card').forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault();

            const checkbox = this.querySelector('input[type="checkbox"]');
            const id = parseInt(checkbox.value);

            if (checkbox.checked) {
                checkbox.checked = false;
                this.classList.remove('selected');
                sectoresSeleccionados = sectoresSeleccionados.filter(s => s !== id);
                delete problemasSeleccionados[id];
            } else {
                if (sectoresSeleccionados.length >= 3) {
                    showToast('Máximo 3 sectores permitidos', 'Límite alcanzado', 'error');
                    return;
                }
                checkbox.checked = true;
                this.classList.add('selected');
                sectoresSeleccionados.push(id);
            }
            updateSectorCounter();
        });
    });
}

function updateSectorCounter() {
    const counter = document.getElementById('sectorCounter');
    if (counter) {
        counter.textContent = `${sectoresSeleccionados.length}/3 seleccionados`;
        if (sectoresSeleccionados.length === 3) {
            counter.classList.add('text-warning');
            counter.classList.remove('text-muted');
        } else {
            counter.classList.remove('text-warning');
            counter.classList.add('text-muted');
        }
    }
}

function initCharCounter() {
    const textarea = document.getElementById('propuesta');
    const counter = document.getElementById('charCount');

    if (textarea && counter) {
        textarea.addEventListener('input', function() {
            counter.textContent = this.value.length;
            if (this.value.length > 450) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    }
}

function updateProgress(step) {
    const totalSteps = 5;
    const progress = (step / totalSteps) * 100;
    document.getElementById('progressBar').style.width = progress + '%';
    
    document.querySelectorAll('.step-indicator').forEach((el, index) => {
        if (index + 1 < step) {
            el.classList.add('completed');
            el.classList.remove('active');
        } else if (index + 1 === step) {
            el.classList.add('active');
            el.classList.remove('completed');
        } else {
            el.classList.remove('active', 'completed');
        }
    });
}

function showLoading(btn, loading = true) {
    if (loading) {
        btn.disabled = true;
        btn.dataset.originalHtml = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cargando...';
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalHtml;
    }
}

function nextStep(step) {
    if (step === 2 && sectoresSeleccionados.length === 0) {
        showToast('Selecciona al menos un sector', 'Campo requerido', 'error');
        return;
    }

    if (step === 2) {
        loadProblemas();
    }

    if (step === 3) {
        const hasAtLeastOne = sectoresSeleccionados.some(id => problemasSeleccionados[id]);
        if (!hasAtLeastOne) {
            showToast('Selecciona al menos un problema', 'Campo requerido', 'error');
            return;
        }
        loadPrioridadConProblemas();
    }

    if (step === 4) {
        const sectorRadio = document.querySelector('input[name="sectorPrioridad"]:checked');
        if (!sectorRadio) {
            showToast('Selecciona el sector prioritario', 'Campo requerido', 'error');
            return;
        }
        loadPropuestaForm();
    }

    if (step === 5) {
        const hasAtLeastOne = sectoresSeleccionados.some(id => problemasSeleccionados[id]);
        if (!hasAtLeastOne) {
            showToast('Selecciona al menos un problema', 'Campo requerido', 'error');
            prevStep(3);
            return;
        }
    }

    document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
    document.getElementById('step' + step).style.display = 'block';
    updateProgress(step);
    
    document.querySelector('.form-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function prevStep(step) {
    document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
    document.getElementById('step' + step).style.display = 'block';
    updateProgress(step);
}

async function loadProblemas() {
    const container = document.getElementById('problemasContainer');
    container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Cargando problemas...</p></div>';

    try {
        let html = '';

        for (const sectorId of sectoresSeleccionados) {
            const card = document.querySelector(`[data-id="${sectorId}"]`);
            const sectorNombre = card ? card.querySelector('label span').textContent : `Sector ${sectorId}`;

            const response = await fetch(`${apiUrls.problemas}${sectorId}`);
            const problemas = await response.json();

            const selectedProblem = problemasSeleccionados[sectorId] || null;

            html += `
                <div class="mb-4">
                    <h6 class="fw-bold text-muted mb-3">
                        <i class="bi bi-folder-fill me-2"></i>${escapeHtml(sectorNombre)}
                    </h6>
                    <div class="problemas-grid" data-sector-group="${sectorId}">
            `;

            problemas.forEach(p => {
                const safeName = escapeHtml(p.nombre);
                const isSelected = selectedProblem === safeName;
                html += `
                    <div class="problema-card ${isSelected ? 'selected' : ''}" 
                         data-nombre="${safeName}" data-sector-id="${sectorId}" 
                         onclick="selectProblema(this, ${sectorId})">
                        <div class="problema-icon"><i class="bi bi-exclamation-triangle"></i></div>
                        <div class="problema-name">${safeName}</div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar problemas.</div>';
    }
}

function selectProblema(element, sectorId) {
    const group = element.closest('.problemas-grid');
    if (group) {
        group.querySelectorAll('.problema-card').forEach(card => card.classList.remove('selected'));
    }
    element.classList.add('selected');
    problemasSeleccionados[sectorId] = element.dataset.nombre;
}

async function loadPrioridadConProblemas() {
    const container = document.getElementById('prioridadContainer');
    container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Cargando opciones...</p></div>';

    try {
        let html = '';
        
        for (const sectorId of sectoresSeleccionados) {
            const card = document.querySelector(`[data-id="${sectorId}"]`);
            const sectorNombre = card ? card.querySelector('label span').textContent : `Sector ${sectorId}`;
            
            const response = await fetch(`${apiUrls.problemas}${sectorId}`);
            const problemas = await response.json();
            
            const isExpanded = sectoresSeleccionados.indexOf(sectorId) === 0;
            const selectedProblem = problemasSeleccionados[sectorId] || null;

            html += `
                <div class="sector-prioridad-section mb-4 ${isExpanded ? 'expanded' : ''}" data-sector-id="${sectorId}">
                    <div class="sector-prioridad-header" onclick="toggleSectorProblemas(this, event)">
                        <div class="d-flex align-items-center">
                            <input class="form-check-input me-3" type="radio" name="sectorPrioridad" 
                                   value="${sectorId}" id="prioridad${sectorId}" 
                                   ${isExpanded ? 'checked' : ''}
                                   onclick="event.stopPropagation()">
                            <h6 class="mb-0 fw-bold">${escapeHtml(sectorNombre)}</h6>
                            ${selectedProblem ? '<span class="badge bg-success ms-2"><i class="bi bi-check-lg"></i> Seleccionado</span>' : ''}
                        </div>
                        <i class="bi bi-chevron-down toggle-icon"></i>
                    </div>
                    <div class="sector-prioridad-body" id="sectorProblemas${sectorId}" style="display: ${isExpanded ? 'block' : 'none'};">
                        <div class="problemas-prioridad-grid">
            `;
            
            problemas.forEach(p => {
                const safeName = escapeHtml(p.nombre);
                const isSelected = selectedProblem === safeName;
                html += `
                    <div class="problema-prioridad-card ${isSelected ? 'selected' : ''}" 
                         data-nombre="${safeName}" 
                         onclick="selectProblemaPrioridad(this, ${sectorId})">
                        <i class="bi bi-check-circle-fill text-success ${isSelected ? '' : 'd-none'} check-icon"></i>
                        <span>${safeName}</span>
                    </div>
                `;
            });
            
            html += `
                            <div class="problema-prioridad-card custom-problema" onclick="toggleCustomPrioridad(${sectorId})">
                                <i class="bi bi-plus-circle"></i>
                                <span>Otro</span>
                            </div>
                        </div>
                        <div class="custom-prioridad-input mt-2" id="customPrioridad${sectorId}" style="display: none;">
                            <input type="text" class="form-control form-control-sm" 
                                   placeholder="Escribe un problema personalizado..." 
                                   data-sector="${sectorId}" maxlength="200">
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += `
            <div class="alert alert-info alert-sm mt-3">
                <i class="bi bi-info-circle me-2"></i>
                <small>Selecciona el sector que consideras más importante y opcionalmente escribe un problema específico.</small>
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar opciones.</div>';
    }
}

function toggleSectorProblemas(header, event) {
    if (event) event.stopPropagation();

    const section = header.closest('.sector-prioridad-section');
    const body = section.querySelector('.sector-prioridad-body');
    const isExpanded = section.classList.contains('expanded');

    document.querySelectorAll('.sector-prioridad-section').forEach(s => {
        if (s !== section) {
            s.classList.remove('expanded');
            s.querySelector('.sector-prioridad-body').style.display = 'none';
        }
    });

    if (isExpanded) {
        section.classList.remove('expanded');
        body.style.display = 'none';
    } else {
        section.classList.add('expanded');
        body.style.display = 'block';
    }
}

function selectProblemaPrioridad(element, sectorId) {
    const body = document.getElementById(`sectorProblemas${sectorId}`);
    body.querySelectorAll('.problema-prioridad-card').forEach(card => {
        card.classList.remove('selected');
        card.querySelector('.check-icon')?.classList.add('d-none');
    });
    
    element.classList.add('selected');
    element.querySelector('.check-icon')?.classList.remove('d-none');
    
    document.getElementById(`customPrioridad${sectorId}`).style.display = 'none';
    
    problemasSeleccionados[sectorId] = element.dataset.nombre;

    document.querySelectorAll('.sector-prioridad-section').forEach(s => {
        const sId = parseInt(s.dataset.sectorId);
        if (sId === sectorId) {
            const header = s.querySelector('.sector-prioridad-header');
            const existingBadge = header.querySelector('.badge');
            if (existingBadge) existingBadge.remove();
            header.querySelector('.d-flex').insertAdjacentHTML('beforeend', 
                '<span class="badge bg-success ms-2"><i class="bi bi-check-lg"></i> Seleccionado</span>');
        }
    });
}

function toggleCustomPrioridad(sectorId) {
    const input = document.getElementById(`customPrioridad${sectorId}`);
    const allInputs = document.querySelectorAll('.custom-prioridad-input');
    
    allInputs.forEach(i => {
        if (i.id !== `customPrioridad${sectorId}`) {
            i.style.display = 'none';
        }
    });
    
    if (input.style.display === 'none' || !input.style.display) {
        input.style.display = 'block';
        input.querySelector('input').focus();
    } else {
        input.style.display = 'none';
    }
}

function selectTipoPropuesta(element) {
    document.querySelectorAll('.tipo-propuesta-card').forEach(card => card.classList.remove('selected'));
    element.classList.add('selected');
    tipoPropuesta = element.dataset.tipo;
}

function loadPropuestaForm() {
    const container = document.getElementById('propuestaContainer');
    const titleEl = document.getElementById('step4Title');
    const subtitleEl = document.getElementById('step4Subtitle');

    if (tipoPropuesta === 'por_sector' && sectoresSeleccionados.length > 1) {
        titleEl.textContent = 'Propuestas por sector';
        subtitleEl.textContent = 'Escribe una propuesta para cada sector que seleccionaste.';

        let html = '';

        if (sectoresSeleccionados.length > 1) {
            html += `
                <div class="mb-4">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card p-3 tipo-propuesta-card selected" data-tipo="unificada" onclick="selectTipoPropuesta(this); loadPropuestaForm();">
                                <div class="d-flex align-items-start">
                                    <i class="bi bi-chat-left-text text-primary fs-3 me-3"></i>
                                    <div>
                                        <h6 class="fw-bold mb-1">Propuesta unificada</h6>
                                        <small class="text-muted">Una sola propuesta que aborde todos los sectores.</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card p-3 tipo-propuesta-card" data-tipo="por_sector" onclick="selectTipoPropuesta(this); loadPropuestaForm();">
                                <div class="d-flex align-items-start">
                                    <i class="bi bi-grid-3x3-gap text-primary fs-3 me-3"></i>
                                    <div>
                                        <h6 class="fw-bold mb-1">Propuesta por sector</h6>
                                        <small class="text-muted">Escribe una propuesta separada para cada sector.</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <hr class="my-3">
            `;
        }

        for (const sectorId of sectoresSeleccionados) {
            const card = document.querySelector(`[data-id="${sectorId}"]`);
            const sectorNombre = card ? card.querySelector('label span').textContent : `Sector ${sectorId}`;
            html += `
                <div class="mb-4">
                    <label class="form-label fw-bold">
                        <i class="bi bi-folder-fill me-2 text-primary"></i>${escapeHtml(sectorNombre)}
                    </label>
                    <textarea class="form-control propuesta-sector-textarea" rows="3"
                              maxlength="500" data-sector-id="${sectorId}"
                              placeholder="Escribe tu propuesta para el sector ${escapeHtml(sectorNombre)}..."></textarea>
                    <div class="d-flex justify-content-between mt-1">
                        <small class="text-muted"><i class="bi bi-lightbulb me-1"></i>Sé específico y claro</small>
                        <small><span class="char-count fw-bold">0</span>/500</small>
                    </div>
                </div>
            `;
        }
        container.innerHTML = html;

        container.querySelectorAll('.propuesta-sector-textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.nextElementSibling.querySelector('.char-count').textContent = this.value.length;
                if (this.value.length > 450) {
                    this.nextElementSibling.querySelector('.char-count').classList.add('text-danger');
                } else {
                    this.nextElementSibling.querySelector('.char-count').classList.remove('text-danger');
                }
            });
        });
    } else {
        tipoPropuesta = 'unificada';
        titleEl.textContent = 'Tu propuesta';

        let subtitle = 'Escribe tu propuesta concreta para resolver el problema identificado.';
        let typeChooser = '';

        if (sectoresSeleccionados.length > 1) {
            subtitle = 'Elige el tipo de propuesta y escribe tu respuesta.';
            typeChooser = `
                <div class="mb-4">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card p-3 tipo-propuesta-card selected" data-tipo="unificada" onclick="selectTipoPropuesta(this); loadPropuestaForm();">
                                <div class="d-flex align-items-start">
                                    <i class="bi bi-chat-left-text text-primary fs-3 me-3"></i>
                                    <div>
                                        <h6 class="fw-bold mb-1">Propuesta unificada</h6>
                                        <small class="text-muted">Una sola propuesta que aborde todos los sectores.</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card p-3 tipo-propuesta-card" data-tipo="por_sector" onclick="selectTipoPropuesta(this); loadPropuestaForm();">
                                <div class="d-flex align-items-start">
                                    <i class="bi bi-grid-3x3-gap text-primary fs-3 me-3"></i>
                                    <div>
                                        <h6 class="fw-bold mb-1">Propuesta por sector</h6>
                                        <small class="text-muted">Escribe una propuesta separada para cada sector.</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <hr class="my-3">
            `;
        }

        subtitleEl.textContent = subtitle;
        container.innerHTML = `
            ${typeChooser}
            <div class="form-group">
                <textarea class="form-control form-control-lg" id="propuesta" rows="5"
                          maxlength="500" placeholder="Ejemplo: Crear incentivos tributarios para empresas que contraten jóvenes sin experiencia."></textarea>
                <div class="d-flex justify-content-between mt-2">
                    <small class="text-muted"><i class="bi bi-lightbulb me-1"></i>Sé específico y claro</small>
                    <small><span id="charCount" class="fw-bold">0</span>/500</small>
                </div>
            </div>
        `;
        initCharCounter();
    }
}

function getPropuestas() {
    if (tipoPropuesta === 'por_sector' && sectoresSeleccionados.length > 1) {
        const textareas = document.querySelectorAll('.propuesta-sector-textarea');
        const propuestas = [];
        textareas.forEach(textarea => {
            propuestas.push({
                sector_id: parseInt(textarea.dataset.sectorId),
                propuesta: textarea.value.trim()
            });
        });
        return { tipo: 'por_sector', propuestas };
    } else {
        const textarea = document.getElementById('propuesta');
        return { tipo: 'unificada', propuestas: [{ propuesta: textarea?.value || '' }] };
    }
}

async function enviarParticipacion() {
    const btn = document.getElementById('btnEnviar');
    showLoading(btn, true);

    const prioridadRadio = document.querySelector('input[name="sectorPrioridad"]:checked');
    
    const problemaPrincipal = problemasSeleccionados[prioridadRadio ? parseInt(prioridadRadio.value) : sectoresSeleccionados[0]] || 'No especificado';

    const customPrioridadInputs = document.querySelectorAll('.custom-prioridad-input input');
    let problemaPrioridadCustom = null;
    customPrioridadInputs.forEach(input => {
        if (input.value.trim()) {
            problemaPrioridadCustom = input.value.trim();
        }
    });

    const propuestasData = getPropuestas();

    const data = {
        sectores: sectoresSeleccionados,
        sector_prioritario_id: prioridadRadio ? parseInt(prioridadRadio.value) : sectoresSeleccionados[0],
        problema_principal: problemaPrioridadCustom || problemaPrincipal,
        problema_otro: '',
        tipo_propuesta: propuestasData.tipo,
        propuestas: propuestasData.propuestas,
        propuesta: propuestasData.propuestas[0]?.propuesta || '',
        departamento: document.getElementById('departamento').value,
        municipio: document.getElementById('municipio').value,
        rango_edad: document.getElementById('rango_edad').value,
        genero: document.getElementById('genero').value
    };

    try {
        const response = await fetch(apiUrls.enviar, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('¡Participación registrada exitosamente!', 'Éxito', 'success');
            if (typeof launchConfetti === 'function') {
                launchConfetti();
            }
            setTimeout(() => {
                window.location.href = apiUrls.confirmacion;
            }, 2000);
        } else {
            showToast(result.error || 'Error al enviar', 'Error', 'error');
            showLoading(btn, false);
        }
    } catch (error) {
        showToast('Error de conexión. Intenta de nuevo.', 'Error', 'error');
        showLoading(btn, false);
    }
}
