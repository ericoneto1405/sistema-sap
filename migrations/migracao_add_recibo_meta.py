from meu_app import create_app, db
from meu_app.models import Pagamento

def run():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    # SQLite: ALTER TABLE ADD COLUMN para cada novo campo
    conn = db.engine.connect()
    try:
        conn.execute(db.text("ALTER TABLE pagamento ADD COLUMN recibo_mime VARCHAR(50)"))
    except Exception:
        pass
    try:
        conn.execute(db.text("ALTER TABLE pagamento ADD COLUMN recibo_tamanho INTEGER"))
    except Exception:
        pass
    try:
        conn.execute(db.text("ALTER TABLE pagamento ADD COLUMN recibo_sha256 VARCHAR(64)"))
    except Exception:
        pass
    try:
        conn.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS ux_pagamento_recibo_sha256 ON pagamento(recibo_sha256)"))
    except Exception:
        pass
    try:
        conn.execute(db.text("ALTER TABLE pagamento ADD COLUMN ocr_json TEXT"))
    except Exception:
        pass
    try:
        conn.execute(db.text("ALTER TABLE pagamento ADD COLUMN ocr_confidence NUMERIC(5,2)"))
    except Exception:
        pass
    conn.close()
    ctx.pop()

if __name__ == "__main__":
    run()


