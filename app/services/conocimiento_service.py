"""Servicio de contenido del Centro de Conocimiento Público (F2).

Provee el contenido educativo estructurado que se renderiza en la
página única ``/conocer``: concepto de política pública, ciclo de vida
interactivo, instrumentos del Estado, glosario interconectado y casos
reales colombianos.
"""
from __future__ import annotations

from typing import Any

MODULO1 = {
    "titulo": "¿Qué es una política pública?",
    "resumen": (
        "Una política pública es una decisión del Estado, respaldada por un plan y "
        "recursos, para resolver un problema que afecta a la sociedad. No es solo un "
        "documento: es un ciclo que combina evidencia, decisiones, acciones y "
        "evaluación continua."
    ),
    "ingredientes": [
        {
            "icono": "bi-clipboard-data",
            "titulo": "Evidencia",
            "texto": "Se apoya en datos, diagnósticos y estudios, no en opiniones sueltas.",
        },
        {
            "icono": "bi-people",
            "titulo": "Participación",
            "texto": "Incluye a ciudadanía, expertos e instituciones en su construcción.",
        },
        {
            "icono": "bi-diagram-3",
            "titulo": "Gestión",
            "texto": "Define responsables, plazos, presupuesto y mecanismos de seguimiento.",
        },
    ],
    "caso_practico": {
        "titulo": "Caso práctico: las basuras del barrio",
        "pasos": [
            "Vecinos reportan acumulación de residuos y riesgos de salud.",
            "La alcaldía hace un diagnóstico: frecuencia, rutas y costos.",
            "Se formula un plan de recolección y educación ciudadana con presupuesto.",
            "El plan se implementa, se hace seguimiento y se ajusta cada año.",
        ],
    },
}

CICLO_POLITICA = [
    {
        "numero": 1,
        "titulo": "Problema",
        "pregunta_clave": "¿Qué está pasando y a quién afecta?",
        "entregable": "Definición clara del problema público.",
    },
    {
        "numero": 2,
        "titulo": "Agenda",
        "pregunta_clave": "¿Este problema entra a la agenda del Estado?",
        "entregable": "El problema se prioriza oficialmente.",
    },
    {
        "numero": 3,
        "titulo": "Diagnóstico",
        "pregunta_clave": "¿Cuáles son las causas y la magnitud?",
        "entregable": "Evidencia y datos sobre el problema.",
    },
    {
        "numero": 4,
        "titulo": "Formulación",
        "pregunta_clave": "¿Qué se va a hacer y con qué recursos?",
        "entregable": "Objetivos, acciones, responsables y presupuesto.",
    },
    {
        "numero": 5,
        "titulo": "Implementación",
        "pregunta_clave": "¿Cómo se ejecuta en el territorio?",
        "entregable": "Acciones en marcha con operadores y cronograma.",
    },
    {
        "numero": 6,
        "titulo": "Seguimiento",
        "pregunta_clave": "¿Se está cumpliendo el plan?",
        "entregable": "Indicadores y reportes periódicos.",
    },
    {
        "numero": 7,
        "titulo": "Evaluación",
        "pregunta_clave": "¿Funcionó? ¿Qué resultados reales hubo?",
        "entregable": "Informe de resultados e impacto.",
    },
    {
        "numero": 8,
        "titulo": "Mejoramiento",
        "pregunta_clave": "¿Qué se ajusta para la siguiente ronda?",
        "entregable": "Ajustes al plan o nuevo ciclo.",
    },
]

INSTRUMENTOS = [
    {
        "nombre": "Constitución",
        "jerarquia": "Nivel máximo",
        "que_es": "Norma superior del Estado que define derechos, deberes y estructura del poder público.",
        "ejemplo": "La Constitución de 1991 de Colombia.",
        "slug": "constitucion",
    },
    {
        "nombre": "Ley",
        "jerarquia": "Nivel legislativo",
        "que_es": "Norma expedida por el Congreso que regula derechos y obligaciones.",
        "ejemplo": "La Ley 1955 de 2019, base del Plan Nacional de Desarrollo.",
        "slug": "ley",
    },
    {
        "nombre": "Decreto",
        "jerarquia": "Nivel ejecutivo",
        "que_es": "Norma expedida por el Ejecutivo para reglamentar leyes sin necesidad de trámite legislativo.",
        "ejemplo": "Un decreto que reglamenta la implementación de una ley.",
        "slug": "decreto",
    },
    {
        "nombre": "CONPES",
        "jerarquia": "Nivel de planeación",
        "que_es": "Documento de política del Consejo Nacional de Política Económica y Social, con diagnóstico y acciones.",
        "ejemplo": "El CONPES 4126 sobre ciencia, tecnología e innovación.",
        "slug": "conpes",
    },
    {
        "nombre": "Plan Nacional de Desarrollo (PND)",
        "jerarquia": "Nivel de planeación",
        "que_es": "Instrumento que orienta la política pública del Gobierno para el cuatrienio.",
        "ejemplo": "El PND 2027-2030 que se construye con la ciudadanía.",
        "slug": "pnd",
    },
    {
        "nombre": "Política Pública sectorial",
        "jerarquia": "Nivel de planeación",
        "que_es": "Conjunto de decisiones y acciones coordinadas para un tema o sector específico.",
        "ejemplo": "La Política Pública de Primera Infancia.",
        "slug": "politica-sectorial",
    },
    {
        "nombre": "Programa / Proyecto",
        "jerarquia": "Nivel operativo",
        "que_es": "Conjunto de actividades con objetivos, presupuesto y responsables para materializar una política.",
        "ejemplo": "Un programa de entrega de vivienda de interés social.",
        "slug": "programa-proyecto",
    },
    {
        "nombre": "Plan territorial",
        "jerarquia": "Nivel territorial",
        "que_es": "Instrumento de los gobiernos departamentales y municipales que recoge el PND en su territorio.",
        "ejemplo": "El Plan de Desarrollo Municipal.",
        "slug": "plan-territorial",
    },
    {
        "nombre": "ODS",
        "jerarquia": "Nivel global",
        "que_es": "Los 17 Objetivos de Desarrollo Sostenible de la ONU que orientan las agendas públicas.",
        "ejemplo": "El ODS 11: ciudades y comunidades sostenibles.",
        "slug": "ods",
    },
]

GLOSARIO = [
    {
        "termino": "Política pública",
        "definicion": "Decisión del Estado con plan, recursos y evaluación para resolver un problema social.",
        "relacionados": ["PND", "CONPES", "Agenda"],
    },
    {
        "termino": "Agenda",
        "definicion": "Lista de problemas que el Estado reconoce y prioriza para actuar.",
        "relacionados": ["Política pública", "Diagnóstico"],
    },
    {
        "termino": "Diagnóstico",
        "definicion": "Análisis con evidencia de las causas y la magnitud de un problema público.",
        "relacionados": ["Agenda", "Evidencia"],
    },
    {
        "termino": "Evidencia",
        "definicion": "Datos, estudios e información verificable que sustentan las decisiones públicas.",
        "relacionados": ["Diagnóstico", "Evaluación"],
    },
    {
        "termino": "Indicador",
        "definicion": "Medida que permite verificar el avance o resultado de una política.",
        "relacionados": ["Seguimiento", "Evaluación"],
    },
    {
        "termino": "Seguimiento",
        "definicion": "Verificación periódica de que el plan se ejecuta según lo previsto.",
        "relacionados": ["Indicador", "Evaluación"],
    },
    {
        "termino": "Evaluación",
        "definicion": "Valoración de resultados e impactos reales de una política para aprender y mejorar.",
        "relacionados": ["Seguimiento", "Evidencia"],
    },
    {
        "termino": "PND",
        "definicion": "Plan Nacional de Desarrollo: instrumento que orienta la política del Gobierno por cuatrienio.",
        "relacionados": ["Política pública", "CONPES", "Plan territorial"],
    },
    {
        "termino": "CONPES",
        "definicion": "Documento de política del Consejo Nacional de Política Económica y Social.",
        "relacionados": ["PND", "Política pública"],
    },
    {
        "termino": "Plan territorial",
        "definicion": "Instrumento de alcaldías y gobernaciones que aterriza las políticas en cada territorio.",
        "relacionados": ["PND", "Política pública"],
    },
    {
        "termino": "Presupuesto",
        "definicion": "Recursos asignados por el Estado para financiar una política o programa.",
        "relacionados": ["Programa / Proyecto", "Formulación"],
    },
    {
        "termino": "Formulación",
        "definicion": "Etapa donde se definen objetivos, acciones, responsables y recursos de la política.",
        "relacionados": ["Diagnóstico", "Presupuesto"],
    },
]

CASOS_REALES = [
    {
        "titulo": "Política de Ciencia, Tecnología e Innovación",
        "resumen": (
            "El CONPES 4126 definió la hoja de ruta para que Colombia invierta más en "
            "ciencia y tecnología, con metas de inversión y reglas para el uso de "
            "regalías en proyectos de innovación territorial."
        ),
        "fuente": "CONPES 4126 (2023), Departamento Nacional de Planeación.",
    },
    {
        "titulo": "Plan Nacional de Desarrollo 2022-2026",
        "resumen": (
            "El PND 'Colombia Potencia Mundial de la Vida' se construyó con diálogos "
            "regionales, incluyó pactos por territorio y transformó las regalías en "
            "mecanismo de financiación de proyectos locales."
        ),
        "fuente": "Ley 2294 de 2023, Congreso de la República.",
    },
    {
        "titulo": "Política de Primera Infancia",
        "resumen": (
            "Un ejemplo de ciclo completo: de la evidencia sobre desarrollo infantil al "
            "programa 'De Cero a Siempre', con evaluación de impacto y ajustes "
            "permanentes en cobertura y calidad."
        ),
        "fuente": "CONPES 109 de 2007 y desarrollos posteriores.",
    },
]


def obtener_contenido() -> dict[str, Any]:
    """Agrupa todo el contenido del Centro de Conocimiento para su renderizado.

    Returns:
        dict con los bloques modulo1, ciclo, instrumentos, glosario y casos.
    """
    return {
        "modulo1": MODULO1,
        "ciclo": CICLO_POLITICA,
        "instrumentos": INSTRUMENTOS,
        "glosario": GLOSARIO,
        "casos": CASOS_REALES,
    }
