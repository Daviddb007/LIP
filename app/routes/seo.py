"""Rutas de SEO / GEO: sitemap.xml, robots.txt y llms.txt.

Prepara la superficie pública para motores de búsqueda y para los crawlers de
IA (GEO): estructura, citabilidad y descripción en lenguaje claro.
"""
from __future__ import annotations

from flask import Blueprint, Response, url_for

seo_bp = Blueprint("seo", __name__)

# URLs públicas indexables (endpoint, prioridad, cambio)
_PAGINAS = [
    ("home.index", "1.0", "weekly"),
    ("home.presentacion", "0.4", "monthly"),
    ("consultoria.pagina", "0.8", "weekly"),
    ("secop.pagina", "0.9", "daily"),
    ("secop.licitar", "0.8", "weekly"),
    ("iniciativa.iniciativa", "0.8", "monthly"),
    ("participar.participar", "0.8", "monthly"),
    ("conocimiento.pagina", "0.7", "monthly"),
    ("biblioteca.lista", "0.7", "monthly"),
    ("resultados.resultados", "0.7", "weekly"),
    ("analitica.pagina", "0.7", "monthly"),
    ("asistente.pagina", "0.7", "monthly"),
    ("armonizacion.pagina", "0.6", "monthly"),
    ("laboratorio.pagina", "0.6", "monthly"),
    ("nosotros.pagina", "0.5", "yearly"),
    ("saas.landing", "0.5", "monthly"),
    ("saas.registro", "0.4", "yearly"),
    ("legal.tratamiento_datos", "0.3", "yearly"),
    ("legal.transparencia", "0.3", "yearly"),
    ("legal.terminos", "0.3", "yearly"),
    ("legal.privacidad", "0.3", "yearly"),
    ("legal.derechos_titulares", "0.3", "yearly"),
    ("legal.cookies", "0.3", "yearly"),
]


@seo_bp.route("/sitemap.xml")
def sitemap():
    urls = []
    for endpoint, priority, freq in _PAGINAS:
        urls.append(
            f"  <url>\n"
            f"    <loc>{url_for(endpoint, _external=True)}</loc>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return Response(xml, mimetype="application/xml")


@seo_bp.route("/robots.txt")
def robots():
    sitemap_url = url_for("seo.sitemap", _external=True)
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: ChatGPT-User\n"
        "Allow: /\n"
        "\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {sitemap_url}\n"
    )
    return Response(body, mimetype="text/plain")


@seo_bp.route("/llms.txt")
def llms():
    body = (
        "# Laboratorio de Inteligencia Pública — Construyamos Colombia\n"
        "\n"
        "> Sistema Nacional de Inteligencia Participativa para la construcción del "
        "Plan Nacional de Desarrollo 2027-2030. Powered by StoneLytics (tecnología SRIE). "
        "Recolectamos, organizamos, clasificamos y transformamos propuestas ciudadanas "
        "en evidencia accionable, y publicamos datos vivos de contratación pública (SECOP II).\n"
        "\n"
        "## Páginas principales\n"
        f"- [Visor SECOP II](/secop): procesos de contratación pública de Colombia con oferta abierta — {url_for('secop.pagina', _external=True)}. Filtros por departamento, modalidad, valor, fecha y pilar PND; actualizado a diario desde datos.gov.co.\n"
        f"- [Servicio de licitación pública](/secop/licitar): ayudamos a empresas a empezar a licitar con el Estado (RUP, búsqueda de oportunidades, preparación de propuestas). {url_for('secop.licitar', _external=True)}\n"
        f"- [Consultoría para entidades públicas](/consultoria): diagnóstico e inteligencia para municipios, gobernaciones y entidades centralizadas (participación, datos, observatorio, contratación, motor SRIE). {url_for('consultoria.pagina', _external=True)}\n"
        f"- [Participa](/participar): registra una propuesta ciudadana para el PND 2027-2030. {url_for('participar.participar', _external=True)}\n"
        f"- [Biblioteca de políticas](/biblioteca): políticas públicas colombianas navegables. {url_for('biblioteca.lista', _external=True)}\n"
        f"- [Resultados](/resultados): lo que Colombia está diciendo — observatorio ciudadano. {url_for('resultados.resultados', _external=True)}\n"
        f"- [Analítica](/analitica): series, territorio y tendencias. {url_for('analitica.pagina', _external=True)}\n"
        f"- [Asistente SRIE](/asistente): respuestas sobre el Estado colombiano con fuentes oficiales. {url_for('asistente.pagina', _external=True)}\n"
        f"- [Conocer](/conocer): cómo funciona una política pública, en lenguaje ciudadano. {url_for('conocimiento.pagina', _external=True)}\n"
        f"- [Presentación](/presentacion): deck público del Laboratorio de Inteligencia Pública. {url_for('home.presentacion', _external=True)}\n"
        "\n"
        "## Contacto\n"
        "- Email: daviddb@stonelytics.tech\n"
        "- Web: https://www.stonelytics.tech\n"
    )
    return Response(body, mimetype="text/plain; charset=utf-8")
