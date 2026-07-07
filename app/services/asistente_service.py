from __future__ import annotations

import re
import unicodedata

CONOCIMIENTO: list[dict] = [
    {
        'categoria': 'entidades',
        'palabras_clave': ['presidencia', 'presidente', 'casa de nariño', 'jefe de estado', 'gobierno nacional', 'ramas del poder'],
        'preguntas': ['¿qué hace la presidencia?', '¿quién es el presidente?', '¿cómo funciona la presidencia?', 'poder ejecutivo'],
        'respuesta': 'La Presidencia de la República es la máxima autoridad del poder ejecutivo en Colombia. El Presidente es Jefe de Estado, Jefe de Gobierno y Suprema Autoridad Administrativa. Sus funciones incluyen: dirigir las relaciones internacionales, sancionar y promulgar leyes, declarar estados de excepción, y ser Comandante Supremo de las Fuerzas Militares.',
    },
    {
        'categoria': 'entidades',
        'palabras_clave': ['ministerio', 'ministerios', 'cartera ministerial', 'gabinete', 'sector administrativo'],
        'preguntas': ['¿qué ministerios existen?', '¿cuántos ministerios hay?', '¿qué hace un ministerio?', 'carteras ministeriales'],
        'respuesta': 'Colombia cuenta con 18 ministerios que conforman el gabinete del Gobierno Nacional. Cada ministerio lidera un sector específico: Interior, Relaciones Exteriores, Hacienda, Justicia, Defensa, Agricultura, Salud, Trabajo, Minas y Energía, Comercio, Educación, Ambiente, Vivienda, TIC, Transporte, Cultura, Deporte, y Ciencia. Los ministerios diseñan y ejecutan las políticas públicas de su sector.',
    },
    {
        'categoria': 'entidades',
        'palabras_clave': ['congreso', 'senado', 'cámara', 'representantes', 'poder legislativo', 'parlamento', 'legisladores'],
        'preguntas': ['¿qué hace el congreso?', '¿cómo funciona el congreso?', 'senado y cámara', 'quién hace las leyes'],
        'respuesta': 'El Congreso de la República es el poder legislativo de Colombia. Está conformado por dos cámaras: el Senado (108 senadores elegidos por voto popular) y la Cámara de Representantes (188 representantes). Sus funciones principales son: aprobar leyes, reformar la Constitución, ejercer control político sobre el gobierno y aprobar el presupuesto nacional.',
    },
    {
        'categoria': 'entidades',
        'palabras_clave': ['corte constitucional', 'corte suprema', 'consejo de estado', 'poder judicial', 'justicia', 'jueces', 'ramas judicial'],
        'preguntas': ['¿cómo funciona la justicia?', '¿qué hace la corte constitucional?', 'poder judicial en colombia', 'altas cortes'],
        'respuesta': 'El poder judicial en Colombia está conformado por cuatro altas cortes: la Corte Constitucional (vigila que las leyes estén alineadas con la Constitución), la Corte Suprema de Justicia (máximo tribunal penal, civil y laboral), el Consejo de Estado (máximo tribunal contencioso administrativo) y el Consejo Superior de la Judicatura (administra la rama judicial).',
    },
    {
        'categoria': 'entidades',
        'palabras_clave': ['dnp', 'departamento nacional de planeación', 'planeación nacional', 'planeacion'],
        'preguntas': ['¿qué hace el dnp?', 'departamento nacional de planeación', 'planeación nacional', 'quién hace el pnd'],
        'respuesta': 'El Departamento Nacional de Planeación (DNP) es la entidad técnica del Gobierno Nacional responsable de diseñar, coordinar y hacer seguimiento al Plan Nacional de Desarrollo (PND). También prepara los documentos CONPES, evalúa las políticas públicas, diseña el presupuesto de inversión y lidera la agenda de desarrollo territorial. El DNP es clave en la formulación de la visión de largo plazo del país.',
    },
    {
        'categoria': 'entes',
        'palabras_clave': ['dane', 'estadísticas', 'censo', 'información estadística', 'datos oficiales'],
        'preguntas': ['¿qué hace el dane?', 'estadísticas oficiales', 'censo colombia', 'datos demográficos'],
        'respuesta': 'El Departamento Administrativo Nacional de Estadística (DANE) es la entidad responsable de producir y difundir las estadísticas oficiales de Colombia. Entre sus funciones están: realizar el censo nacional de población, medir el desempleo a través de la GEIH, calcular el Índice de Precios al Consumidor (IPC), medir la pobreza multidimensional y producir cuentas nacionales. Sus datos son insumo fundamental para la formulación de políticas públicas.',
    },
    {
        'categoria': 'entidades',
        'palabras_clave': ['dps', 'prosperidad social', 'departamento prosperidad', 'programas sociales', 'superación pobreza'],
        'preguntas': ['¿qué hace prosperidad social?', 'dps programas', 'ayudas sociales', 'beneficios económicos'],
        'respuesta': 'El Departamento para la Prosperidad Social (DPS) es la entidad del Gobierno Nacional encargada de diseñar, coordinar y ejecutar programas de asistencia social para la superación de la pobreza. Administra programas como Familias en Acción, Jóvenes en Acción, Colombia Mayor, Ingreso Solidario y la Red Unidos. Su objetivo es reducir la pobreza y la desigualdad en Colombia.',
    },
    {
        'categoria': 'instrumentos',
        'palabras_clave': ['pnd', 'plan nacional de desarrollo', 'plan de desarrollo', 'hoja de ruta', 'plan gobierno'],
        'preguntas': ['¿qué es el pnd?', 'plan nacional de desarrollo', 'qué dice el pnd', 'plan de desarrollo colombia'],
        'respuesta': 'El Plan Nacional de Desarrollo (PND) es el instrumento de planeación más importante del Gobierno Nacional. Se elabora cada 4 años al inicio del período presidencial y define las prioridades, metas, inversiones y políticas públicas que guiarán al país durante el cuatrienio. El PND es aprobado por el Congreso de la República y su cumplimiento es evaluado anualmente. El PND 2027-2030 establece las bases del desarrollo social, económico y ambiental de Colombia.',
    },
    {
        'categoria': 'instrumentos',
        'palabras_clave': ['conpes', 'documento conpes', 'consejo política económica', 'política económica y social'],
        'preguntas': ['¿qué es un conpes?', 'documento conpes', 'cómo funciona conpes', 'política conpes'],
        'respuesta': 'El Documento CONPES es un instrumento de política aprobado por el Consejo Nacional de Política Económica y Social (CONPES). Este consejo está integrado por el Presidente, todos los ministros y directores de departamentos administrativos. Los documentos CONPES establecen lineamientos estratégicos para sectores específicos, asignan recursos y definen responsables. Ejemplos: CONPES de política de economía naranja, CONPES de cambio climático o CONPES de primera infancia.',
    },
    {
        'categoria': 'instrumentos',
        'palabras_clave': ['ley', 'leyes', 'proyecto de ley', 'aprobación de ley', 'norma', 'legislación'],
        'preguntas': ['¿cómo se hace una ley?', 'proceso legislativo', 'aprobación de leyes', 'qué es una ley'],
        'respuesta': 'Una ley en Colombia es una norma aprobada por el Congreso de la República y sancionada por el Presidente. El proceso incluye: 1) presentación del proyecto por congresistas o gobierno, 2) debate en comisiones del Senado y Cámara, 3) debate en plenarias de ambas cámaras (4 debates), 4) conciliación entre versiones, 5) sanción presidencial y 6) publicación. Las leyes tienen el rango más alto después de la Constitución y pueden crear derechos, obligaciones e instituciones.',
    },
    {
        'categoria': 'instrumentos',
        'palabras_clave': ['decreto', 'decretos', 'reglamentación', 'norma ejecutiva', 'presidente decreta'],
        'preguntas': ['¿qué es un decreto?', 'decretos presidenciales', 'diferencia entre ley y decreto'],
        'respuesta': 'Un decreto es una norma emitida por el Presidente de la República para reglamentar leyes o ejercer funciones ejecutivas. A diferencia de las leyes, los decretos no requieren aprobación del Congreso. Existen varios tipos: decretos reglamentarios (detallan cómo se aplica una ley), decretos legislativos (durante estados de excepción) y decretos ordinarios (funciones administrativas). Los decretos tienen fuerza de ley y son de obligatorio cumplimiento.',
    },
    {
        'categoria': 'instrumentos',
        'palabras_clave': ['constitución', 'constitución política', 'carta magna', 'constitución 1991', 'norma suprema'],
        'preguntas': ['¿qué dice la constitución?', 'constitución de 1991', 'derechos fundamentales', 'carta política colombia'],
        'respuesta': 'La Constitución Política de Colombia de 1991 es la norma suprema del Estado colombiano. Establece los derechos y deberes de los ciudadanos, la organización del Estado, la división de poderes, los mecanismos de participación ciudadana y las garantías constitucionales. La Constitución es la ley de leyes: ninguna norma puede estar por encima de ella. Ha tenido más de 60 reformas desde su expedición.',
    },
    {
        'categoria': 'participacion',
        'palabras_clave': ['participar', 'cómo participar', 'participación ciudadana', 'mecanismos participación', 'votar', 'consulta'],
        'preguntas': ['¿cómo puedo participar?', 'participación ciudadana', 'mecanismos de participación', 'cómo influir en decisiones'],
        'respuesta': 'En Colombia existen múltiples mecanismos de participación ciudadana. Los más importantes son: el voto (elecciones cada 4 años), el plebiscito (consulta popular para aprobar o rechazar decisiones), el referendo (aprobación de normas por voto popular), la consulta popular (decisión sobre asuntos territoriales), el cabildo abierto (discusión pública con autoridades), la iniciativa legislativa (propuestas ciudadanas de ley) y la revocatoria del mandato. Además, plataformas como Laboratorio de Inteligencia Pública permiten participar en la construcción de políticas públicas.',
    },
    {
        'categoria': 'participacion',
        'palabras_clave': ['construyamos colombia', 'plataforma', 'ecosistema', 'stonelytics', 'participar construir'],
        'preguntas': ['¿qué es construyamos colombia?', 'cómo participar en construyamos colombia', 'stonelytics', 'políticas públicas'],
        'respuesta': 'Laboratorio de Inteligencia Pública es el primer Ecosistema Nacional de Inteligencia Pública desarrollado por StoneLytics con tecnología SRIE. Su objetivo es conectar la participación ciudadana con el conocimiento, la evidencia y la toma de decisiones públicas. Puedes participar de forma anónima y sin registro: ingresa a la sección "Participar", selecciona los temas que te interesan, describe los problemas que identificas y propón soluciones. Tu participación es analizada por el motor SRIE y convertida en inteligencia estratégica.',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['política pública', 'políticas públicas', 'qué es política pública', 'política social', 'políticas estado'],
        'preguntas': ['¿qué es una política pública?', 'políticas públicas en colombia', 'cómo se hace una política pública'],
        'respuesta': 'Una política pública es una decisión del Estado que busca resolver un problema que afecta a la sociedad. No es una simple idea, sino un plan de acción con recursos, responsables y plazos concretos. Una política pública incluye: un diagnóstico del problema, objetivos claros, población beneficiaria, entidades responsables, presupuesto asignado, indicadores de medición y mecanismos de evaluación. En Colombia, las políticas públicas pueden adoptar forma de leyes, CONPES, decretos o programas sectoriales.',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['presupuesto', 'presupuesto nacional', 'presupuesto general', 'recursos públicos', 'inversión pública', 'pgn'],
        'preguntas': ['¿cómo se asigna el presupuesto?', 'presupuesto nacional colombia', 'quién aprueba el presupuesto', 'pgn'],
        'respuesta': 'El Presupuesto General de la Nación (PGN) es el instrumento que define cuánto y en qué gasta el Estado colombiano cada año. Lo propone el Ministerio de Hacienda, lo ajusta el CONPES y lo aprueba el Congreso de la República. Se divide en: funcionamiento (salarios, gastos operativos), inversión (proyectos, infraestructura, programas sociales) y servicio de la deuda. Para 2026, el PGN supera los $500 billones de pesos.',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['vivienda', 'subsidio vivienda', 'casa propia', 'mi casa ya', 'vivienda interés social'],
        'preguntas': ['políticas de vivienda', 'subsidio de vivienda colombia', 'mi casa ya', 'cómo comprar vivienda con subsidio'],
        'respuesta': 'La política de vivienda en Colombia está liderada por el Ministerio de Vivienda. El programa principal es "Mi Casa Ya", que otorga un subsidio a la cuota inicial (hasta $30 millones) y una cobertura a la tasa de interés para créditos hipotecarios. Está dirigido a hogares con ingresos hasta 4 salarios mínimos. También existe el programa de Vivienda de Interés Social (VIS) y Vivienda de Interés Prioritario (VIP) para los hogares de menores ingresos. Más de 300.000 familias han sido beneficiadas.',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['educación', 'educación superior', 'colegio', 'universidad', 'becas', 'matrícula', 'gratuidad'],
        'preguntas': ['política educativa colombia', 'educación gratuita', 'becas para estudiar', 'matrícula cero', 'educación superior'],
        'respuesta': 'Colombia cuenta con la política de "Gratuidad en la Educación Superior" que permite estudiar sin pagar matrícula en instituciones públicas. El programa cubre el 100% de la matrícula para estudiantes de estratos 1, 2 y 3. Además, el ICETEX ofrece créditos educativos y becas para estudios superiores. En educación básica, el Ministerio de Educación promueve la Jornada Única Escolar (7 horas diarias), la alimentación escolar y la calidad educativa a través de programas como "Colegios de Calidad".',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['salud', 'eps', 'servicios de salud', 'sistema de salud', 'médico', 'hospital', 'medicamentos'],
        'preguntas': ['cómo funciona la salud en colombia', 'eps colombia', 'sistema de salud colombiano', 'atención médica'],
        'respuesta': 'El sistema de salud en Colombia se rige por la Ley 100 de 1993. Está compuesto por dos regímenes: contributivo (trabajadores formales que cotizan) y subsidiado (personas sin capacidad de pago, financiado por el Estado). Las EPS (Entidades Promotoras de Salud) son las aseguradoras que gestionan los servicios, y las IPS (Instituciones Prestadoras de Salud) son los hospitales y clínicas que atienden a los pacientes. La Superintendencia de Salud vigila el sistema.',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['seguridad', 'defensa', 'fuerzas militares', 'policía', 'orden público', 'conflicto', 'violencia'],
        'preguntas': ['política de seguridad colombia', 'fuerzas militares', 'policía nacional', 'seguridad ciudadana', 'defensa nacional'],
        'respuesta': 'La seguridad en Colombia está a cargo del Ministerio de Defensa, que coordina las Fuerzas Militares (Ejército, Armada, Fuerza Aérea) y la Policía Nacional. Las Fuerzas Militares se encargan de la defensa y soberanía nacional, mientras que la Policía es responsable de la seguridad ciudadana. La política de seguridad incluye estrategias contra el crimen organizado, el narcotráfico, la minería ilegal y los grupos armados. También existen políticas de paz y posconflicto tras el Acuerdo de Paz de 2016.',
    },
    {
        'categoria': 'politicas',
        'palabras_clave': ['ambiente', 'medio ambiente', 'cambio climático', 'sostenible', 'conservación', 'ecología', 'naturaleza'],
        'preguntas': ['política ambiental colombia', 'cambio climático colombia', 'qué hace el ministerio de ambiente', 'conservación'],
        'respuesta': 'La política ambiental de Colombia es liderada por el Ministerio de Ambiente y Desarrollo Sostenible. Incluye la Política Nacional de Cambio Climático que busca reducir emisiones de CO₂ en un 51% para 2030 y alcanzar la carbono neutralidad a 2050. Otras políticas importantes son: la conservación de parques naturales, la lucha contra la deforestación, la gestión integral de residuos, la protección del recurso hídrico y la promoción de energías renovables. Colombia es uno de los países más biodiversos del mundo.',
    },
    {
        'categoria': 'general',
        'palabras_clave': ['construyamos colombia', 'ecosistema', 'inteligencia pública', 'srie'],
        'preguntas': ['asistente', 'quién eres', 'qué puedes hacer', 'ayuda'],
        'respuesta': 'Soy el Asistente Público SRIE, un especialista en el Estado colombiano desarrollado por StoneLytics como parte del Ecosistema Nacional de Inteligencia Pública "Laboratorio de Inteligencia Pública". Puedo responder preguntas sobre: cómo funciona el Estado colombiano, qué son las políticas públicas, qué entidades existen, cómo participar, qué instrumentos de planeación hay (PND, CONPES, leyes), y las políticas públicas en sectores como educación, salud, vivienda, ambiente y seguridad. Toda mi información proviene de fuentes oficiales y está verificada.',
    },
]


def normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    return texto


def responder(pregunta: str) -> dict:
    pregunta_norm = normalizar(pregunta)

    mejor_puntaje = 0
    mejor_respuesta = None

    for item in CONOCIMIENTO:
        puntaje = 0

        for keyword in item['palabras_clave']:
            kw_norm = normalizar(keyword)
            if kw_norm in pregunta_norm:
                puntaje += 3

        for q in item['preguntas']:
            q_norm = normalizar(q)
            coincidencias = len(set(pregunta_norm.split()) & set(q_norm.split()))
            puntaje += coincidencias * 1.5 * (2 if len(pregunta_norm.split()) > 2 else 1)

        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_respuesta = item

    if mejor_puntaje >= 2:
        return {
            'tiene_respuesta': True,
            'respuesta': mejor_respuesta['respuesta'],
            'categoria': mejor_respuesta['categoria'],
            'confianza': min(100, int((mejor_puntaje / 10) * 100)),
        }

    return {
        'tiene_respuesta': False,
        'respuesta': 'Lo siento, aún no tengo información suficiente para responder esa pregunta con precisión. '
                     'Estoy aprendiendo continuamente sobre el Estado colombiano. '
                     'Puedes intentar reformular tu pregunta o consultar el Centro de Conocimiento y la Biblioteca Inteligente.',
        'categoria': None,
        'confianza': 0,
    }
