"""Punto de entrada para la aplicación.

Uso:
    python run.py              # Servidor de desarrollo
    flask seed                 # Sembrar datos iniciales (plan + catálogos)
    flask init-db              # Crear tablas sin seed
    flask db migrate           # Generar migración
    flask db upgrade           # Aplicar migración
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db


app = create_app(os.environ.get("FLASK_CONFIG", "development"))


@app.cli.command("seed")
def seed_command():
    """Crea tablas y siembra datos iniciales (plan + sectores + actores + beneficiarios)."""
    with app.app_context():
        db.create_all()
        from app.seed import run_all

        run_all()


@app.cli.command("migrate-v2")
def migrate_v2_command():
    """Migra participaciones desde la base de datos V2 a V3."""
    from app.cli.migrate_v2 import run_migration

    with app.app_context():
        stats = run_migration(dry_run=False)
        print(f"Migración completada: {stats['participaciones']} participaciones, "
              f"{stats['clasificaciones']} clasificaciones, "
              f"{stats['errores']} errores, {stats['saltados']} saltados")


@app.cli.command("init-db")
def init_db_command():
    """Crea todas las tablas sin sembrar datos."""
    with app.app_context():
        db.create_all()
        print("Tablas creadas exitosamente.")


@app.cli.command("migrate-consent")
def migrate_consent_command():
    """Añade columnas de consentimiento a base de datos existente (idempotente)."""
    from datetime import datetime, timezone
    from sqlalchemy import inspect, text as sa_text

    with app.app_context():
        inspector = inspect(db.engine)
        columns = {c["name"] for c in inspector.get_columns("participaciones")}
        added = []

        if "consentimiento_aceptado" not in columns:
            db.session.execute(sa_text(
                "ALTER TABLE participaciones ADD COLUMN consentimiento_aceptado BOOLEAN NOT NULL DEFAULT FALSE"
            ))
            added.append("consentimiento_aceptado")
        if "consentimiento_version" not in columns:
            db.session.execute(sa_text(
                "ALTER TABLE participaciones ADD COLUMN consentimiento_version VARCHAR(20) NOT NULL DEFAULT '2026-01'"
            ))
            added.append("consentimiento_version")
        if "consentimiento_at" not in columns:
            db.session.execute(sa_text(
                "ALTER TABLE participaciones ADD COLUMN consentimiento_at TIMESTAMP"
            ))
            added.append("consentimiento_at")
        if "anonimizada" not in columns:
            db.session.execute(sa_text(
                "ALTER TABLE participaciones ADD COLUMN anonimizada BOOLEAN NOT NULL DEFAULT FALSE"
            ))
            added.append("anonimizada")

        db.session.commit()
        if added:
            print(f"Columnas añadidas: {', '.join(added)}")
        else:
            print("No se requirieron cambios. Las columnas ya existen.")


@app.cli.command("anonimizar-datos")
def anonimizar_datos_command():
    """Anonimiza participaciones que han superado la fecha de retención."""
    from datetime import datetime, timezone

    with app.app_context():
        retention_until = app.config.get("DATA_RETENTION_UNTIL", "2030-12-31")
        try:
            cutoff = datetime.strptime(retention_until, "%Y-%m-%d").replace(tzinfo=None)
        except ValueError:
            print(f"Error: DATA_RETENTION_UNTIL inválido ({retention_until}). Use formato YYYY-MM-DD.")
            return

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if now < cutoff:
            print(f"Aún no se requiere anonimizar. Fecha de retención: {retention_until}")
            return

        from app.models.participacion import Participacion

        expired = Participacion.query.filter(
            Participacion.anonimizada == False,
            Participacion.created_at < cutoff,
        ).all()

        count = 0
        for p in expired:
            p.justificacion = ""
            p.propuesta = ""
            p.ip_hash = None
            p.municipio = ""
            p.rango_edad = None
            p.genero = None
            p.anonimizada = True
            count += 1

        db.session.commit()
        print(f"{count} participaciones anonimizadas.")


@app.cli.command("transcribir-pendientes")
def transcribir_pendientes_command():
    """Procesa sincrónicamente los audios de grupos focales pendientes (fallback sin Redis)."""
    from app.models.focal import AudioFocal
    from app.services.transcripcion_service import procesar_audio

    with app.app_context():
        pendientes = AudioFocal.query.filter(
            AudioFocal.estado.in_(["pendiente", "error"])
        ).order_by(AudioFocal.id).all()

        if not pendientes:
            print("No hay audios pendientes.")
            return

        for audio in pendientes:
            print(f"Transcribiendo audio #{audio.id} ({audio.nombre_original})...")
            resultado = procesar_audio(audio.id)
            estado = "OK" if resultado["ok"] else "ERROR"
            print(f"  -> {estado}: {resultado}")


@app.cli.command("construir-grafos")
def construir_grafos_command():
    """Construye grafos de conocimiento para sesiones transcritas sin grafo."""
    from app.models.focal import SesionFocal
    from app.services.grafo_service import construir_grafo

    with app.app_context():
        sesiones = SesionFocal.query.all()
        for sesion in sesiones:
            if not sesion.transcript:
                continue
            from app.models.grafo import NodoGrafo

            tiene_nodos = NodoGrafo.query.filter_by(sesion_id=sesion.id).first()
            if tiene_nodos:
                print(f"Sesión #{sesion.id}: grafo ya construido")
                continue
            resultado = construir_grafo(sesion.transcript.id)
            if resultado["ok"]:
                print(f"Sesión #{sesion.id}: {resultado['nodos']} nodos, temas: {resultado['temas']}")
            else:
                print(f"Sesión #{sesion.id}: ERROR {resultado.get('error')}")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=app.config.get("PORT", 5000))
