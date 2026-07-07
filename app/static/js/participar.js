let apiUrls = {};
let conversationData = {
    sectores: [],
    problemas: {},
    sectorPrioritarioId: null,
    problemaPrincipal: '',
    contextoCiudadano: '',
    propuesta: '',
    actoresResponsables: '',
    beneficiarios: '',
    departamento: '',
    municipio: '',
    rangoEdad: '',
    genero: ''
};
let currentStep = 'welcome';
let allSectores = [];
let allProblemas = {};

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', function() {
    apiUrls = {
        problemas: document.getElementById('apiProblemasUrl')?.value || '/api/problemas/',
        enviar: document.getElementById('apiEnviarUrl')?.value || '/api/enviar',
        clasificar: document.getElementById('apiClasificarUrl')?.value || '/api/clasificar',
        confirmacion: document.getElementById('apiConfirmacionUrl')?.value || '/confirmacion'
    };

    const input = document.getElementById('txtInput');
    if (input) {
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            document.getElementById('charCountFooter').textContent = this.value.length;
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarTexto();
            }
        });
    }

    loadSectores();
});

async function loadSectores() {
    try {
        const response = await fetch('/api/sectores');
        allSectores = await response.json();

        for (const s of allSectores) {
            const res = await fetch(`${apiUrls.problemas}${s.id}`);
            allProblemas[s.id] = await res.json();
        }
    } catch (e) {
        console.error('Error loading sectors:', e);
    }
}

function scrollToBottom() {
    const body = document.getElementById('conversacionBody');
    setTimeout(() => {
        body.scrollTop = body.scrollHeight;
    }, 100);
}

function addMessage(content, type = 'assistant') {
    const body = document.getElementById('conversacionBody');
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${type}-bubble animate-in`;
    bubble.innerHTML = content;
    body.appendChild(bubble);
    scrollToBottom();
    return bubble;
}

function showTyping() {
    document.getElementById('loadingIndicator').style.display = 'flex';
    document.getElementById('inputContainer').style.display = 'none';
    scrollToBottom();
}

function hideTyping() {
    document.getElementById('loadingIndicator').style.display = 'none';
    document.getElementById('inputContainer').style.display = 'block';
}

function showTextInput(placeholder = 'Escribe tu respuesta aquí...') {
    document.getElementById('inputOptions').style.display = 'none';
    document.getElementById('inputText').style.display = 'block';
    const input = document.getElementById('txtInput');
    input.placeholder = placeholder;
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('charCountFooter').textContent = '0';
    document.getElementById('conversacionFooter').style.display = 'block';
    setTimeout(() => input.focus(), 300);
}

function showOptions(options) {
    document.getElementById('inputText').style.display = 'none';
    const container = document.getElementById('inputOptions');
    container.style.display = 'flex';

    let html = '';
    options.forEach((opt, i) => {
        let classes = 'option-btn btn ';
        if (opt.variant === 'primary') {
            classes += 'btn-primary';
        } else if (opt.variant === 'success') {
            classes += 'btn-success';
        } else if (opt.variant === 'outline') {
            classes += 'btn-outline-primary';
        } else {
            classes += 'btn-outline-secondary';
        }
        if (opt.selected) {
            classes += ' selected';
        }
        html += `<button class="${classes}" onclick="handleOptionClick(this, ${i})" data-action="${opt.action || ''}" data-value="${escapeHtml(opt.value || '')}">`;
        if (opt.icon) html += `<i class="bi bi-${opt.icon} me-2"></i>`;
        html += `${escapeHtml(opt.label)}</button>`;
    });
    container.innerHTML = html;
    document.getElementById('conversacionFooter').style.display = 'block';
}

function handleOptionClick(btn, index) {
    const options = btn.parentElement.querySelectorAll('.option-btn');
    const action = btn.dataset.action;

    if (action === 'toggle-sector') {
        btn.classList.toggle('selected');
        return;
    }
    if (action === 'toggle-problema') {
        options.forEach(o => o.classList.remove('selected'));
        btn.classList.add('selected');
        return;
    }
    if (action === 'next') {
        const actionFn = btn.dataset.value;
        if (typeof window[actionFn] === 'function') {
            window[actionFn]();
        }
        return;
    }
}

function iniciarConversacion() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-2"><strong>¡Genial!</strong> Primero, cuéntame ¿sobre qué temas te gustaría hablar?</p>
            <p class="mb-0 text-muted small">Puedes seleccionar hasta 3 temas de la lista.</p>
        </div>
    `);

    showTyping();
    setTimeout(() => {
        hideTyping();
        renderSectorSelection();
        currentStep = 'sectores';
    }, 800);
}

function renderSectorSelection() {
    let optionsHtml = '';
    allSectores.forEach(s => {
        const selected = conversationData.sectores.includes(s.id) ? 'selected' : '';
        optionsHtml += `<button class="option-btn btn btn-outline-secondary ${selected}" onclick="toggleSector(this, ${s.id})" data-action="toggle-sector">
            <i class="bi bi-${s.icono || 'folder'} me-2"></i>${escapeHtml(s.nombre)}
        </button>`;
    });

    const container = document.getElementById('inputOptions');
    container.style.display = 'flex';
    container.innerHTML = `
        <div class="sector-options-grid">
            ${optionsHtml}
        </div>
        <div class="w-100 text-center mt-3">
            <small class="text-muted" id="sectorCountMsg">${conversationData.sectores.length}/3 seleccionados</small>
            <button class="btn btn-primary ms-3" onclick="confirmarSectores()" id="btnConfirmSectores">
                <i class="bi bi-arrow-right me-1"></i>Continuar
            </button>
        </div>
    `;
    document.getElementById('inputText').style.display = 'none';
    document.getElementById('conversacionFooter').style.display = 'block';
}

function toggleSector(btn, id) {
    const idx = conversationData.sectores.indexOf(id);
    if (idx >= 0) {
        conversationData.sectores.splice(idx, 1);
        btn.classList.remove('selected');
    } else if (conversationData.sectores.length < 3) {
        conversationData.sectores.push(id);
        btn.classList.add('selected');
    } else {
        showToast('Máximo 3 temas permitidos', 'Límite alcanzado', 'error');
        return;
    }
    document.getElementById('sectorCountMsg').textContent = `${conversationData.sectores.length}/3 seleccionados`;
}

function confirmarSectores() {
    if (conversationData.sectores.length === 0) {
        showToast('Selecciona al menos un tema', 'Campo requerido', 'error');
        return;
    }

    const nombres = conversationData.sectores.map(id => {
        const s = allSectores.find(s => s.id === id);
        return s ? s.nombre : '';
    }).filter(Boolean);

    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">¡Gracias! Has seleccionado: <strong>${nombres.join(', ')}</strong>.</p>
        </div>
    `);

    showTyping();
    setTimeout(() => {
        hideTyping();
        renderProblemasStep();
    }, 600);
}

function renderProblemasStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">Ahora, para cada tema, ¿cuál es el problema más importante que identificas?</p>
        </div>
    `);

    showTyping();
    setTimeout(() => {
        hideTyping();
        renderProblemasSelection();
        currentStep = 'problemas';
    }, 600);
}

function renderProblemasSelection() {
    let html = '';
    conversationData.sectores.forEach(sectorId => {
        const sector = allSectores.find(s => s.id === sectorId);
        const problemas = allProblemas[sectorId] || [];
        const selected = conversationData.problemas[sectorId] || '';

        html += `<div class="problema-step-group mb-3">
            <h6 class="fw-bold mb-2"><i class="bi bi-folder-fill me-2 text-primary"></i>${escapeHtml(sector ? sector.nombre : '')}</h6>
            <div class="d-flex flex-wrap gap-2">`;

        problemas.forEach(p => {
            const isSel = selected === p.nombre ? 'selected' : '';
            html += `<button class="option-btn btn btn-outline-secondary ${isSel}" onclick="selectProblema(this, ${sectorId}, '${escapeHtml(p.nombre)}')">
                ${escapeHtml(p.nombre)}
            </button>`;
        });

        html += `<button class="option-btn btn btn-outline-secondary ${selected && !problemas.find(p => p.nombre === selected) ? 'selected' : ''}" onclick="selectProblemaCustom(${sectorId})">
            <i class="bi bi-pencil me-1"></i>Otro
        </button>`;

        html += `</div></div>`;
    });

    html += `<div class="w-100 text-center mt-3">
        <button class="btn btn-primary" onclick="confirmarProblemas()">
            <i class="bi bi-arrow-right me-1"></i>Continuar
        </button>
    </div>`;

    const container = document.getElementById('inputOptions');
    container.style.display = 'flex';
    container.innerHTML = html;
    document.getElementById('inputText').style.display = 'none';
    document.getElementById('conversacionFooter').style.display = 'block';
}

function selectProblema(btn, sectorId, nombre) {
    const group = btn.closest('.problema-step-group');
    group.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    conversationData.problemas[sectorId] = nombre;
}

function selectProblemaCustom(sectorId) {
    const group = document.querySelector(`.problema-step-group:nth-child(${conversationData.sectores.indexOf(sectorId) + 1})`);
    group.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));

    const answer = prompt('Describe el problema que identificas:');
    if (answer && answer.trim()) {
        conversationData.problemas[sectorId] = answer.trim();

        const customBtn = Array.from(group.querySelectorAll('.option-btn')).find(b => b.textContent.includes('Otro'));
        if (customBtn) customBtn.classList.add('selected');
    }
}

function confirmarProblemas() {
    const sinProblema = conversationData.sectores.some(id => !conversationData.problemas[id]);
    if (sinProblema) {
        showToast('Selecciona un problema para cada tema', 'Campo requerido', 'error');
        return;
    }

    let detalles = '';
    conversationData.sectores.forEach(id => {
        const sector = allSectores.find(s => s.id === id);
        detalles += `<li><strong>${escapeHtml(sector ? sector.nombre : '')}:</strong> ${escapeHtml(conversationData.problemas[id])}</li>`;
    });

    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">Perfecto. Estos son los problemas que identificaste:</p>
            <ul class="mb-1">${detalles}</ul>
        </div>
    `);

    showTyping();
    setTimeout(() => {
        hideTyping();
        renderContextoStep();
    }, 600);
}

function renderContextoStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">Cuéntame, <strong>¿por qué crees que ocurre este problema?</strong> ¿Hay algo en tu experiencia o en tu comunidad que ayude a entenderlo mejor?</p>
            <p class="mb-0 text-muted small">Describe brevemente el contexto que conoces.</p>
        </div>
    `);

    showTextInput('Ej: En mi barrio falta inversión en alcantarillado desde hace 10 años...');
    currentStep = 'contexto';
}

function enviarTexto() {
    const input = document.getElementById('txtInput');
    const text = input.value.trim();
    if (!text) return;

    addMessage(`
        <div class="message-avatar user-avatar"><i class="bi bi-person-fill"></i></div>
        <div class="message-content user-content">
            <p class="mb-0">${escapeHtml(text)}</p>
        </div>
    `, 'user');

    input.value = '';
    input.style.height = 'auto';
    document.getElementById('charCountFooter').textContent = '0';
    document.getElementById('inputText').style.display = 'none';
    document.getElementById('conversacionFooter').style.display = 'none';

    processTextInput(text);
}

function processTextInput(text) {
    switch (currentStep) {
        case 'contexto':
            conversationData.contextoCiudadano = text;
            showTyping();
            setTimeout(() => {
                hideTyping();
                renderPropuestaStep();
            }, 600);
            break;
        case 'propuesta':
            conversationData.propuesta = text;
            showTyping();
            setTimeout(() => {
                hideTyping();
                renderActoresStep();
            }, 600);
            break;
        case 'actores':
            conversationData.actoresResponsables = text;
            showTyping();
            setTimeout(() => {
                hideTyping();
                renderBeneficiariosStep();
            }, 600);
            break;
        case 'beneficiarios':
            conversationData.beneficiarios = text;
            showTyping();
            setTimeout(() => {
                hideTyping();
                renderUbicacionStep();
            }, 600);
            break;
        case 'ubicacion':
            conversationData.departamento = text;
            showTyping();
            setTimeout(() => {
                hideTyping();
                renderFinalStep();
            }, 600);
            break;
    }
}

function renderPropuestaStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">Muy valioso ese contexto. Ahora, <strong>¿qué propones concretamente para solucionar este problema?</strong></p>
            <p class="mb-0 text-muted small">Describe tu propuesta de forma clara y específica.</p>
        </div>
    `);

    showTextInput('Ej: Crear un programa de subsidios para mejoramiento de vivienda...');
    currentStep = 'propuesta';
}

function renderActoresStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">Buena propuesta. <strong>¿Quiénes crees que deberían ser los responsables de implementarla?</strong></p>
            <p class="mb-0 text-muted small">Ej: La alcaldía municipal, el Ministerio de Vivienda, la comunidad organizada...</p>
        </div>
    `);

    showTextInput('Ej: La gobernación departamental y las juntas de acción comunal...');
    currentStep = 'actores';
}

function renderBeneficiariosStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">¿Y <strong>quiénes serían los beneficiarios</strong> de esta propuesta?</p>
            <p class="mb-0 text-muted small">Ej: Jóvenes entre 18 y 25 años, campesinos de la región, madres cabezas de hogar...</p>
        </div>
    `);

    showTextInput('Ej: Familias en situación de pobreza del departamento...');
    currentStep = 'beneficiarios';
}

function renderUbicacionStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-1">Para cerrar, cuéntanos <strong>¿desde qué parte de Colombia nos escribes?</strong></p>
            <p class="mb-0 text-muted small">Esta información nos ayuda a hacer análisis territorial. Es opcional.</p>
        </div>
    `);

    const container = document.getElementById('inputOptions');
    container.style.display = 'flex';
    container.innerHTML = `
        <div class="w-100">
            <div class="row g-2">
                <div class="col-md-6">
                    <select class="form-select" id="selDepartamento">
                        <option value="">Selecciona tu departamento</option>
                        <option value="Amazonas">Amazonas</option>
                        <option value="Antioquia">Antioquia</option>
                        <option value="Arauca">Arauca</option>
                        <option value="Atlántico">Atlántico</option>
                        <option value="Bolívar">Bolívar</option>
                        <option value="Boyacá">Boyacá</option>
                        <option value="Caldas">Caldas</option>
                        <option value="Caquetá">Caquetá</option>
                        <option value="Casanare">Casanare</option>
                        <option value="Cauca">Cauca</option>
                        <option value="Cesar">Cesar</option>
                        <option value="Chocó">Chocó</option>
                        <option value="Córdoba">Córdoba</option>
                        <option value="Cundinamarca">Cundinamarca</option>
                        <option value="Guainía">Guainía</option>
                        <option value="Guaviare">Guaviare</option>
                        <option value="Huila">Huila</option>
                        <option value="La Guajira">La Guajira</option>
                        <option value="Magdalena">Magdalena</option>
                        <option value="Meta">Meta</option>
                        <option value="Nariño">Nariño</option>
                        <option value="Norte de Santander">Norte de Santander</option>
                        <option value="Putumayo">Putumayo</option>
                        <option value="Quindío">Quindío</option>
                        <option value="Risaralda">Risaralda</option>
                        <option value="Santander">Santander</option>
                        <option value="Sucre">Sucre</option>
                        <option value="Tolima">Tolima</option>
                        <option value="Valle del Cauca">Valle del Cauca</option>
                        <option value="Vaupés">Vaupés</option>
                        <option value="Vichada">Vichada</option>
                        <option value="Bogotá D.C.">Bogotá D.C.</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <input type="text" class="form-control" id="txtMunicipio" placeholder="Municipio (opcional)">
                </div>
                <div class="col-12 mt-2">
                    <select class="form-select" id="selEdad">
                        <option value="">Rango de edad (opcional)</option>
                        <option value="16-18">16-18 años</option>
                        <option value="19-25">19-25 años</option>
                        <option value="26-35">26-35 años</option>
                        <option value="36-45">36-45 años</option>
                        <option value="46-55">46-55 años</option>
                        <option value="56-65">56-65 años</option>
                        <option value="66+">66+ años</option>
                    </select>
                </div>
            </div>
            <div class="text-center mt-3">
                <button class="btn btn-primary" onclick="confirmarUbicacion()">
                    <i class="bi bi-arrow-right me-1"></i>Continuar
                </button>
                <button class="btn btn-outline-secondary ms-2" onclick="saltarUbicacion()">
                    Saltar este paso
                </button>
            </div>
        </div>
    `;
    document.getElementById('inputText').style.display = 'none';
    document.getElementById('conversacionFooter').style.display = 'block';
    currentStep = 'ubicacion';
}

function confirmarUbicacion() {
    const depto = document.getElementById('selDepartamento').value;
    const municipio = document.getElementById('txtMunicipio').value;
    const edad = document.getElementById('selEdad').value;

    conversationData.departamento = depto;
    conversationData.municipio = municipio;
    conversationData.rangoEdad = edad;

    const locStr = depto ? `desde ${municipio ? municipio + ', ' : ''}${depto}` : '';
    addMessage(`
        <div class="message-avatar user-avatar"><i class="bi bi-person-fill"></i></div>
        <div class="message-content user-content">
            <p class="mb-0">${locStr || 'Prefiero no decirlo'}</p>
        </div>
    `, 'user');

    showTyping();
    setTimeout(() => {
        hideTyping();
        renderFinalStep();
    }, 600);
}

function saltarUbicacion() {
    addMessage(`
        <div class="message-avatar user-avatar"><i class="bi bi-person-fill"></i></div>
        <div class="message-content user-content">
            <p class="mb-0">Prefiero continuar sin compartir ubicación</p>
        </div>
    `, 'user');

    showTyping();
    setTimeout(() => {
        hideTyping();
        renderFinalStep();
    }, 600);
}

function renderFinalStep() {
    addMessage(`
        <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
        <div class="message-content">
            <p class="mb-2"><strong>¡Hemos terminado!</strong> Revisemos tus respuestas antes de enviar:</p>
            <div class="conversation-summary">
                ${conversationData.sectores.map(id => {
                    const s = allSectores.find(s => s.id === id);
                    return `<div class="summary-item"><span class="summary-label">Tema:</span> <span class="summary-value">${escapeHtml(s ? s.nombre : '')}</span></div>
                    <div class="summary-item"><span class="summary-label">Problema:</span> <span class="summary-value">${escapeHtml(conversationData.problemas[id])}</span></div>`;
                }).join('')}
                <div class="summary-item"><span class="summary-label">Contexto:</span> <span class="summary-value">${escapeHtml(conversationData.contextoCiudadano)}</span></div>
                <div class="summary-item"><span class="summary-label">Propuesta:</span> <span class="summary-value">${escapeHtml(conversationData.propuesta)}</span></div>
                <div class="summary-item"><span class="summary-label">Responsables:</span> <span class="summary-value">${escapeHtml(conversationData.actoresResponsables)}</span></div>
                <div class="summary-item"><span class="summary-label">Beneficiarios:</span> <span class="summary-value">${escapeHtml(conversationData.beneficiarios)}</span></div>
                ${conversationData.departamento ? `<div class="summary-item"><span class="summary-label">Ubicación:</span> <span class="summary-value">${escapeHtml(conversationData.departamento)}${conversationData.municipio ? ', ' + escapeHtml(conversationData.municipio) : ''}</span></div>` : ''}
            </div>
        </div>
    `);

    showOptions([
        { label: 'Enviar participación', icon: 'send-fill', action: 'next', value: 'enviarParticipacion', variant: 'success' },
        { label: 'Volver a empezar', icon: 'arrow-counterclockwise', action: 'next', value: 'reiniciarConversacion', variant: 'outline' }
    ]);
    currentStep = 'final';
}

async function enviarParticipacion() {
    document.getElementById('inputOptions').style.display = 'none';
    document.getElementById('conversacionFooter').style.display = 'none';

    showTyping();

    const firstSectorId = conversationData.sectores[0];
    const data = {
        sectores: conversationData.sectores,
        sector_prioritario_id: firstSectorId,
        problema_principal: conversationData.problemas[firstSectorId] || '',
        contexto_ciudadano: conversationData.contextoCiudadano,
        propuesta: conversationData.propuesta,
        actores_responsables: conversationData.actoresResponsables,
        beneficiarios: conversationData.beneficiarios,
        tipo_propuesta: 'unificada',
        departamento: conversationData.departamento,
        municipio: conversationData.municipio,
        rango_edad: conversationData.rangoEdad,
        genero: ''
    };

    try {
        const response = await fetch(apiUrls.enviar, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        hideTyping();

        if (result.success) {
            addMessage(`
                <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
                <div class="message-content">
                    <div class="text-center mb-3">
                        <div style="font-size: 3rem; color: var(--success-color);"><i class="bi bi-check-circle-fill"></i></div>
                        <h5 class="fw-bold mt-2 mb-1">¡Participación registrada!</h5>
                        <p class="text-muted small mb-3">Gracias por contribuir a la inteligencia pública de Colombia.</p>
                    </div>
                    <button class="btn btn-primary w-100" onclick="mostrarClasificacionSRIE(${result.id})">
                        <i class="bi bi-cpu-fill me-2"></i>Ver clasificación SRIE
                    </button>
                </div>
            `);

            if (typeof launchConfetti === 'function') {
                launchConfetti();
            }

            document.getElementById('conversacionFooter').style.display = 'none';
        } else {
            addMessage(`
                <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
                <div class="message-content">
                    <div class="alert alert-danger mb-2">
                        <i class="bi bi-exclamation-triangle me-2"></i>${escapeHtml(result.error || 'Error al enviar')}
                    </div>
                    <button class="btn btn-outline-primary btn-sm" onclick="intentarDeNuevo()">Intentar de nuevo</button>
                </div>
            `);
        }
    } catch (error) {
        hideTyping();
        addMessage(`
            <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
            <div class="message-content">
                <div class="alert alert-danger mb-2">
                    <i class="bi bi-exclamation-triangle me-2"></i>Error de conexión. Intenta de nuevo.
                </div>
                <button class="btn btn-outline-primary btn-sm" onclick="intentarDeNuevo()">Intentar de nuevo</button>
            </div>
        `);
    }
}

function intentarDeNuevo() {
    renderFinalStep();
}

async function mostrarClasificacionSRIE(id) {
    const modal = new bootstrap.Modal(document.getElementById('srieResultModal'));
    modal.show();

    const content = document.getElementById('srieResultContent');

    try {
        const payload = {
            sectores: conversationData.sectores,
            problema_principal: conversationData.problemas[conversationData.sectores[0]],
            propuesta: conversationData.propuesta,
            contexto_ciudadano: conversationData.contextoCiudadano,
            actores_responsables: conversationData.actoresResponsables,
            beneficiarios: conversationData.beneficiarios,
        };

        const response = await fetch(apiUrls.clasificar, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const srie = await response.json();

        content.innerHTML = `
            <div class="srie-result">
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="srie-card" style="border-top: 4px solid ${srie.pilar.color};">
                            <div class="srie-card-icon" style="background: ${srie.pilar.color}20; color: ${srie.pilar.color};">
                                <i class="bi bi-${srie.pilar.icono}"></i>
                            </div>
                            <h6 class="fw-bold mt-2">Pilar Estratégico</h6>
                            <p class="fw-semibold" style="color: ${srie.pilar.color};">${srie.pilar.nombre}</p>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar" style="width: ${srie.pilar.confianza}%; background: ${srie.pilar.color};"></div>
                            </div>
                            <small class="text-muted">Confianza: ${srie.pilar.confianza}%</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="srie-card" style="border-top: 4px solid ${srie.urgencia.color};">
                            <div class="srie-card-icon" style="background: ${srie.urgencia.color}20; color: ${srie.urgencia.color};">
                                <i class="bi bi-exclamation-triangle-fill"></i>
                            </div>
                            <h6 class="fw-bold mt-2">Urgencia</h6>
                            <p class="fw-semibold" style="color: ${srie.urgencia.color};">${srie.urgencia.nivel}</p>
                            <small class="text-muted">${srie.urgencia.descripcion}</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="srie-card" style="border-top: 4px solid ${srie.impacto.color};">
                            <div class="srie-card-icon" style="background: ${srie.impacto.color}20; color: ${srie.impacto.color};">
                                <i class="bi bi-globe-americas"></i>
                            </div>
                            <h6 class="fw-bold mt-2">Impacto</h6>
                            <p class="fw-semibold" style="color: ${srie.impacto.color};">${srie.impacto.nivel}</p>
                            <small class="text-muted">${srie.impacto.descripcion}</small>
                        </div>
                    </div>
                </div>
                <div class="srie-explicacion mt-4 p-3" style="background: #f8fafc; border-radius: 16px;">
                    <h6 class="fw-bold mb-2"><i class="bi bi-info-circle me-1"></i>Explicación</h6>
                    <p class="mb-0 text-secondary" style="line-height: 1.7;">${srie.explicacion.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>
                </div>
            </div>
        `;
    } catch (e) {
        content.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-exclamation-circle text-warning" style="font-size: 3rem;"></i>
                <p class="mt-2 text-muted">No se pudo generar la clasificación en este momento.</p>
            </div>
        `;
    }
}

function reiniciarConversacion() {
    conversationData = {
        sectores: [],
        problemas: {},
        sectorPrioritarioId: null,
        problemaPrincipal: '',
        contextoCiudadano: '',
        propuesta: '',
        actoresResponsables: '',
        beneficiarios: '',
        departamento: '',
        municipio: '',
        rangoEdad: '',
        genero: ''
    };
    currentStep = 'welcome';
    document.getElementById('conversacionBody').innerHTML = `
        <div class="message-bubble assistant-bubble animate-in">
            <div class="message-avatar"><i class="bi bi-chat-dots-fill"></i></div>
            <div class="message-content">
                <p class="mb-1">¡Hola! Soy el asistente de <strong>Laboratorio de Inteligencia Pública</strong>, el Ecosistema Nacional de Inteligencia Pública.</p>
                <p class="mb-1">Te voy a hacer algunas preguntas para entender tu visión y convertir tus ideas en evidencia para la toma de decisiones. No necesitas registrarte y toda tu participación es anónima.</p>
                <p class="mb-0">¿Empezamos?</p>
                <div class="message-actions mt-2">
                    <button class="btn btn-sm btn-primary" onclick="iniciarConversacion()">
                        <i class="bi bi-play-fill me-1"></i>¡Sí, empecemos!
                    </button>
                </div>
            </div>
        </div>
    `;
    document.getElementById('conversacionFooter').style.display = 'none';
}
