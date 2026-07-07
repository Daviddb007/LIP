const GLOSARIO = [
    { termino: 'Política pública', definicion: 'Conjunto de decisiones y acciones del Estado para resolver un problema que afecta a la sociedad. Incluye recursos, responsables, plazos y mecanismos de evaluación.', categoria: 'planeacion', enlaces: ['Plan Nacional de Desarrollo', 'CONPES', 'Indicador'] },
    { termino: 'Plan Nacional de Desarrollo', sigla: 'PND', definicion: 'Instrumento de planeación que define las prioridades, metas e inversiones del gobierno nacional para un período de 4 años. Es la hoja de ruta del país.', categoria: 'planeacion', enlaces: ['Política pública', 'Plan Territorial', 'ODS'] },
    { termino: 'CONPES', definicion: 'Documento de política aprobado por el Consejo Nacional de Política Económica y Social. Establece lineamientos estratégicos para sectores específicos con asignación de recursos.', categoria: 'planeacion', enlaces: ['Política pública', 'Plan Nacional de Desarrollo', 'Indicador'] },
    { termino: 'Ley', definicion: 'Norma aprobada por el Congreso de la República. Tiene el rango más alto después de la Constitución. Crea derechos, obligaciones y modifica instituciones.', categoria: 'normas', enlaces: ['Decreto', 'Política pública', 'Constitución'] },
    { termino: 'Decreto', definicion: 'Norma emitida por el Presidente para reglamentar leyes o ejercer funciones ejecutivas sin necesidad de aprobación del Congreso.', categoria: 'normas', enlaces: ['Ley', 'Política pública'] },
    { termino: 'Constitución', definicion: 'Norma suprema del Estado colombiano. Todas las leyes y políticas públicas deben estar alineadas con lo que establece la Constitución Política de 1991.', categoria: 'normas', enlaces: ['Ley', 'Política pública'] },
    { termino: 'Plan Territorial', sigla: 'PT', definicion: 'Instrumento de planeación de gobernaciones y alcaldías que define las prioridades de desarrollo del territorio, alineado con el PND.', categoria: 'territorio', enlaces: ['Plan Nacional de Desarrollo', 'Política pública', 'Indicador'] },
    { termino: 'ODS', definicion: 'Objetivos de Desarrollo Sostenible de Naciones Unidas. 17 metas globales que Colombia ha adoptado como marco de referencia para sus políticas públicas.', categoria: 'planeacion', enlaces: ['Plan Nacional de Desarrollo', 'Política pública', 'Indicador'] },
    { termino: 'Indicador', definicion: 'Medida cuantitativa que permite evaluar el avance y resultado de una política pública. Responde a: ¿estamos logrando lo que nos propusimos?', categoria: 'evaluacion', enlaces: ['Política pública', 'ODS', 'Plan Nacional de Desarrollo'] },
    { termino: 'Presupuesto', definicion: 'Recursos económicos asignados por el Estado para ejecutar políticas públicas. Se aprueba anualmente y define cuánto se invertirá en cada sector.', categoria: 'planeacion', enlaces: ['Política pública', 'Plan Nacional de Desarrollo', 'Ley'] },
    { termino: 'Población beneficiaria', definicion: 'Grupo de personas que reciben los beneficios directos de una política pública. Pueden ser comunidades, familias o individuos con características específicas.', categoria: 'evaluacion', enlaces: ['Política pública', 'Indicador'] },
    { termino: 'Evaluación de impacto', definicion: 'Estudio que mide si una política pública logró sus objetivos y qué cambios concretos generó en la población beneficiaria.', categoria: 'evaluacion', enlaces: ['Indicador', 'Política pública'] },
    { termino: 'Gobernación', definicion: 'Entidad administrativa que lidera un departamento. Es responsable de ejecutar políticas públicas territoriales y articular con el gobierno nacional.', categoria: 'territorio', enlaces: ['Plan Territorial', 'Política pública', 'Alcaldía'] },
    { termino: 'Alcaldía', definicion: 'Entidad administrativa que lidera un municipio. Es la instancia más cercana al ciudadano y responsable de ejecutar políticas públicas locales.', categoria: 'territorio', enlaces: ['Plan Territorial', 'Política pública', 'Gobernación'] },
    { termino: 'Ministerio', definicion: 'Entidad del gobierno nacional responsable de un sector específico (salud, educación, defensa, etc.). Diseña y ejecuta las políticas públicas del sector.', categoria: 'territorio', enlaces: ['Política pública', 'Ley', 'Presupuesto'] },
    { termino: 'Participación ciudadana', definicion: 'Mecanismo mediante el cual los ciudadanos pueden incidir en las decisiones del Estado. Incluye consultas, audiencias, veedurías y plataformas digitales.', categoria: 'normas', enlaces: ['Política pública', 'Constitución', 'Ley'] },
    { termino: 'Rendición de cuentas', definicion: 'Obligación de las entidades públicas de informar a la ciudadanía sobre sus acciones, resultados y uso de recursos. Fortalece la transparencia.', categoria: 'evaluacion', enlaces: ['Indicador', 'Política pública', 'Participación ciudadana'] },
    { termino: 'Veeduría ciudadana', definicion: 'Mecanismo de control social donde los ciudadanos vigilan la correcta ejecución de recursos públicos y el cumplimiento de políticas.', categoria: 'normas', enlaces: ['Participación ciudadana', 'Rendición de cuentas'] },
];

let currentModule = 'que-es';
let activeGlosarioFilter = 'todas';

document.addEventListener('DOMContentLoaded', function() {
    initModuleNavigation();
    renderGlosario();
    initScrollSpy();
});

function initModuleNavigation() {
    document.querySelectorAll('.knowledge-nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const moduleId = this.dataset.module;

            document.querySelectorAll('.knowledge-nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            document.querySelectorAll('.knowledge-module').forEach(m => m.classList.remove('active'));
            document.getElementById(`modulo-${moduleId}`).classList.add('active');

            currentModule = moduleId;

            setTimeout(() => {
                document.querySelector('.knowledge-content').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        });
    });
}

function toggleInstrument(header) {
    const card = header.closest('.instrument-card');
    const body = card.querySelector('.instrument-body');
    const toggle = card.querySelector('.instrument-toggle');

    if (card.classList.contains('expanded')) {
        card.classList.remove('expanded');
        body.style.display = 'none';
        toggle.style.transform = 'rotate(0deg)';
    } else {
        card.classList.add('expanded');
        body.style.display = 'block';
        toggle.style.transform = 'rotate(180deg)';
    }
}

function expandirCaso(btn) {
    const card = btn.closest('.real-case-card');
    const detail = card.querySelector('.real-case-detail');

    if (detail.style.display === 'none' || !detail.style.display) {
        detail.style.display = 'block';
        btn.innerHTML = '<i class="bi bi-dash-circle me-1"></i>Ver menos';
    } else {
        detail.style.display = 'none';
        btn.innerHTML = '<i class="bi bi-plus-circle me-1"></i>Ver más';
    }
}

function renderGlosario(filtro = 'todas', busqueda = '') {
    const container = document.getElementById('glossaryContainer');

    let terminos = GLOSARIO;

    if (filtro !== 'todas') {
        terminos = terminos.filter(t => t.categoria === filtro);
    }

    if (busqueda) {
        const q = busqueda.toLowerCase();
        terminos = terminos.filter(t =>
            t.termino.toLowerCase().includes(q) ||
            t.definicion.toLowerCase().includes(q)
        );
    }

    if (terminos.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-search text-muted" style="font-size: 3rem;"></i>
                <p class="text-muted mt-3">No encontramos conceptos con ese criterio de búsqueda.</p>
            </div>
        `;
        return;
    }

    let html = '';
    terminos.forEach(t => {
        html += `
            <div class="glossary-card">
                <div class="glossary-card-header">
                    <h5 class="fw-bold mb-1">${t.termino}</h5>
                    ${t.sigla ? `<span class="glossary-sigla">${t.sigla}</span>` : ''}
                    <span class="glossary-category categoria-${t.categoria}">${t.categoria}</span>
                </div>
                <p class="text-secondary small mb-3">${t.definicion}</p>
                ${t.enlaces ? `
                <div class="glossary-enlaces">
                    ${t.enlaces.map(e => `<button class="glossary-enlace" onclick="buscarTermino('${e}')">${e}</button>`).join('')}
                </div>` : ''}
            </div>
        `;
    });

    container.innerHTML = html;
}

function buscarGlosario(value) {
    renderGlosario(activeGlosarioFilter, value);
}

function filtrarGlosario(filtro, btn) {
    document.querySelectorAll('.glossary-tag').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    activeGlosarioFilter = filtro;
    const search = document.getElementById('glossarySearch').value;
    renderGlosario(filtro, search);
}

function buscarTermino(termino) {
    const search = document.getElementById('glossarySearch');
    search.value = termino;

    document.querySelectorAll('.glossary-tag').forEach(t => t.classList.remove('active'));
    document.querySelector('.glossary-tag').classList.add('active');
    activeGlosarioFilter = 'todas';

    renderGlosario('todas', termino);

    document.getElementById('modulo-glosario').closest('.knowledge-module');
    document.querySelectorAll('.knowledge-nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector('[data-module="glosario"]').classList.add('active');
    document.querySelectorAll('.knowledge-module').forEach(m => m.classList.remove('active'));
    document.getElementById('modulo-glosario').classList.add('active');

    setTimeout(() => {
        document.getElementById('glossarySearch').scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 200);
}

function initScrollSpy() {
    const sections = document.querySelectorAll('.knowledge-module');
    const navLinks = document.querySelectorAll('.knowledge-nav-link');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id.replace('modulo-', '');
                navLinks.forEach(l => l.classList.remove('active'));
                const activeLink = document.querySelector(`[data-module="${id}"]`);
                if (activeLink) activeLink.classList.add('active');
            }
        });
    }, { threshold: 0.3 });

    sections.forEach(s => observer.observe(s));
}
