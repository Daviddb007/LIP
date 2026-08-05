"""Motor SRIE — Sistema de Reconocimiento e Inteligencia Estratégica.

Orquesta la clasificación de participaciones contra el marco estratégico activo.
"""
from app.services.srie.classifier import clasificar_participacion

__all__ = ["clasificar_participacion"]
