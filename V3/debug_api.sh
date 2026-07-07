#!/bin/bash
docker exec construyamos_v3_app python3 << 'PYEOF'
from app import create_app
app = create_app("production")
with app.app_context():
    with app.test_client() as c:
        r = c.post("/api/enviar", json={
            "departamento": "Bogota",
            "municipio": "Bogota",
            "zona": "urbana",
            "problema_ids": [7],
            "justificacion": "Test",
            "propuesta": "Test policia",
            "actor_ids": [3],
            "beneficiario_ids": [1]
        })
        print("Status:", r.status_code)
        print("Response:", r.get_data(as_text=True)[:500])
PYEOF
