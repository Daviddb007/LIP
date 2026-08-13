"""Entrypoint del worker RQ (contenedor `worker` de docker-compose).

Escucha las colas de transcripción y análisis. Procesa audios con whisper
local (reserva total) y construye grafos de conocimiento.
"""
import os

from dotenv import load_dotenv
from redis import Redis
from rq import Queue, Worker

load_dotenv()

from app.services.worker_jobs import get_app


def main() -> None:
    app = get_app()
    conn = Redis.from_url(app.config["RQ_CONNECTION_URI"])
    queues = [
        Queue(app.config["RQ_QUEUE_TRANSCRIPCION"], connection=conn),
        Queue(app.config["RQ_QUEUE_ANALISIS"], connection=conn),
    ]
    app.logger.info("Worker RQ iniciado. Colas: %s", [q.name for q in queues])
    Worker(queues).work(with_scheduler=True)


if __name__ == "__main__":
    main()
