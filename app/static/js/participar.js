let sectoresSeleccionados = [];
let sectorPrioritarioId = null;
let problemasSeleccionados = {};
let apiUrls = {};

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
        card.addEventListener('click', function() {
            const checkbox = this.querySelector('input[type="checkbox"]');
            const id = parseInt(checkbox.value);

            if (checkbox.checked) {
                checkbox.checked = false;
                this.classList.remove('selected');
                sectoresSeleccionados = sectoresSeleccionados.filter(s => s !== id);
                updateSectorCounter();
            } else {
                if (sectoresSeleccionados.length >= 3) {
                    showToast('Máximo 3 sectores permitidos', 'Límite alcanzado', 'error');
                    return;
                }
                checkbox.checked = true;
                this.classList.add('selected');
                sectoresSeleccionados.push(id);
                updateSectorCounter();
            }
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
    const progress = (step / 5) * 100;
    document.getElementById('progressBar').style.width = progress + '%';
    
    // Update step indicators
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
        loadPrioridadConProblemas();
    }

    if (step === 4) {
        const problema = document.querySelector('input[name="problema"]:checked');
        const problemaCustom = document.getElementById('problemaCustom')?.value;
        if (!problema && !problemaCustom) {
            showToast('Selecciona o escribe un problema', 'Campo requerido', 'error');
            return;
        }
    }

    document.querySelectorAll('.form-step').forEach(el => el.style.display = 'none');
    document.getElementById('step' + step).style.display = 'block';
    updateProgress(step);
    
    // Scroll to top of form
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
        const primerSector = sectoresSeleccionados[0];
        const response = await fetch(`${apiUrls.problemas}${primerSector}`);
        const problemas = await response.json();

        let html = '<div class="problemas-grid">';
        problemas.forEach(p => {
            html += `
                <div class="problema-card" onclick="selectProblema(this, '${p.nombre}')">
                    <div class="problema-icon"><i class="bi bi-exclamation-triangle"></i></div>
                    <div class="problema-name">${p.nombre}</div>
                </div>
            `;
        });
        html += `
            <div class="problema-card problema-custom" onclick="selectProblemaCustom(this)">
                <div class="problema-icon"><i class="bi bi-pencil-square"></i></div>
                <div class="problema-name">Otro (especificar)</div>
            </div>
        </div>`;

        html += `
            <div id="customProblemaGroup" class="mt-3" style="display: none;">
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-pencil"></i></span>
                    <input type="text" class="form-control" id="problemaCustom" 
                           placeholder="Escribe tu problema aquí..." maxlength="200">
                </div>
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar problemas.</div>';
    }
}

function selectProblema(element, nombre) {
    document.querySelectorAll('.problema-card').forEach(card => card.classList.remove('selected'));
    element.classList.add('selected');
    document.getElementById('customProblemaGroup').style.display = 'none';
    document.getElementById('problemaCustom').value = '';
    problemasSeleccionados['principal'] = nombre;
}

function selectProblemaCustom(element) {
    document.querySelectorAll('.problema-card').forEach(card => card.classList.remove('selected'));
    element.classList.add('selected');
    document.getElementById('customProblemaGroup').style.display = 'block';
    document.getElementById('problemaCustom').focus();
    problemasSeleccionados['principal'] = 'Otro';
}

async function loadPrioridadConProblemas() {
    const container = document.getElementById('prioridadContainer');
    container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Cargando opciones...</p></div>';

    try {
        let html = '';
        
        // For each selected sector, load its problems
        for (const sectorId of sectoresSeleccionados) {
            const card = document.querySelector(`[data-id="${sectorId}"]`);
            const sectorNombre = card ? card.querySelector('label span').textContent : `Sector ${sectorId}`;
            
            const response = await fetch(`${apiUrls.problemas}${sectorId}`);
            const problemas = await response.json();
            
            html += `
                <div class="sector-prioridad-section mb-4">
                    <div class="sector-prioridad-header" onclick="toggleSectorProblemas(${sectorId})">
                        <div class="d-flex align-items-center">
                            <input class="form-check-input me-3" type="radio" name="sectorPrioridad" 
                                   value="${sectorId}" id="prioridad${sectorId}" ${sectorId === sectoresSeleccionados[0] ? 'checked' : ''}>
                            <h6 class="mb-0 fw-bold">${sectorNombre}</h6>
                        </div>
                        <i class="bi bi-chevron-down toggle-icon"></i>
                    </div>
                    <div class="sector-prioridad-body" id="sectorProblemas${sectorId}">
                        <div class="problemas-prioridad-grid">
            `;
            
            problemas.forEach(p => {
                html += `
                    <div class="problema-prioridad-card" onclick="selectProblemaPrioridad(this, ${sectorId}, '${p.nombre}')">
                        <i class="bi bi-check-circle-fill text-success d-none check-icon"></i>
                        <span>${p.nombre}</span>
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
        
        // Set first sector as expanded
        if (sectoresSeleccionados.length > 0) {
            toggleSectorProblemas(sectoresSeleccionados[0]);
        }

    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar opciones.</div>';
    }
}

function toggleSectorProblemas(sectorId) {
    // Toggle the body
    const body = document.getElementById(`sectorProblemas${sectorId}`);
    const allBodies = document.querySelectorAll('.sector-prioridad-body');
    const allHeaders = document.querySelectorAll('.sector-prioridad-header');
    
    allBodies.forEach(b => {
        if (b.id !== `sectorProblemas${sectorId}`) {
            b.style.display = 'none';
            b.closest('.sector-prioridad-section').classList.remove('expanded');
        }
    });
    
    allHeaders.forEach(h => {
        if (h.onclick?.toString().indexOf(sectorId) === -1) {
            h.closest('.sector-prioridad-section').classList.remove('expanded');
        }
    });
    
    if (body.style.display === 'none' || !body.style.display) {
        body.style.display = 'block';
        body.closest('.sector-prioridad-section').classList.add('expanded');
    } else {
        body.style.display = 'none';
        body.closest('.sector-prioridad-section').classList.remove('expanded');
    }
}

function selectProblemaPrioridad(element, sectorId, problemaNombre) {
    // Deselect all problems in this sector
    const body = document.getElementById(`sectorProblemas${sectorId}`);
    body.querySelectorAll('.problema-prioridad-card').forEach(card => {
        card.classList.remove('selected');
        card.querySelector('.check-icon')?.classList.add('d-none');
    });
    
    // Select this one
    element.classList.add('selected');
    element.querySelector('.check-icon')?.classList.remove('d-none');
    
    // Hide custom input
    document.getElementById(`customPrioridad${sectorId}`).style.display = 'none';
    
    // Store selection
    problemasSeleccionados[sectorId] = problemaNombre;
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

async function enviarParticipacion() {
    const btn = document.getElementById('btnEnviar');
    showLoading(btn, true);

    const prioridadRadio = document.querySelector('input[name="sectorPrioridad"]:checked');
    const problemaCustom = document.getElementById('problemaCustom')?.value;
    const problemaSeleccionado = problemasSeleccionados['principal'] || null;
    
    // Get custom problems from priority section
    const customPrioridadInputs = document.querySelectorAll('.custom-prioridad-input input');
    let problemaPrioridadCustom = null;
    customPrioridadInputs.forEach(input => {
        if (input.value.trim()) {
            problemaPrioridadCustom = input.value.trim();
        }
    });

    const data = {
        sectores: sectoresSeleccionados,
        sector_prioritario_id: prioridadRadio ? parseInt(prioridadRadio.value) : sectoresSeleccionados[0],
        problema_principal: problemaCustom || problemaSeleccionado || problemaPrioridadCustom || 'No especificado',
        problema_otro: problemaCustom || '',
        propuesta: document.getElementById('propuesta').value,
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
