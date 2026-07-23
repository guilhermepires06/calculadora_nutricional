from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.sqlite3"

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

DEFAULT_SETTINGS = {
    "brandName": "NutriPlan",
    "brandSubtitle": "Planejamento alimentar",
    "professionalName": "",
    "footerText": "Este material é uma estimativa automática e não substitui avaliação profissional.",
    "logoData": "",
    "theme": "teal",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def init_db() -> None:
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                client_name TEXT NOT NULL DEFAULT 'Sem nome',
                preferences_json TEXT NOT NULL,
                targets_json TEXT NOT NULL,
                plan_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_plans_updated_at
            ON plans(updated_at DESC);

            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                brand_name TEXT NOT NULL,
                brand_subtitle TEXT NOT NULL,
                professional_name TEXT NOT NULL DEFAULT '',
                footer_text TEXT NOT NULL,
                logo_data TEXT NOT NULL DEFAULT '',
                theme TEXT NOT NULL DEFAULT 'teal',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                data_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        existing = db.execute("SELECT id FROM settings WHERE id = 1").fetchone()
        if existing is None:
            db.execute(
                """
                INSERT INTO settings (
                    id, brand_name, brand_subtitle, professional_name,
                    footer_text, logo_data, theme, updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_SETTINGS["brandName"],
                    DEFAULT_SETTINGS["brandSubtitle"],
                    DEFAULT_SETTINGS["professionalName"],
                    DEFAULT_SETTINGS["footerText"],
                    DEFAULT_SETTINGS["logoData"],
                    DEFAULT_SETTINGS["theme"],
                    utc_now(),
                ),
            )


def parse_json_text(value: str, fallback):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


def plan_row_to_dict(row: sqlite3.Row, include_plan: bool = True) -> dict:
    result = {
        "id": row["id"],
        "title": row["title"],
        "clientName": row["client_name"],
        "preferences": parse_json_text(row["preferences_json"], {}),
        "targets": parse_json_text(row["targets_json"], {}),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }
    if include_plan:
        result["plan"] = parse_json_text(row["plan_json"], [])
    return result


def settings_row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "brandName": row["brand_name"],
        "brandSubtitle": row["brand_subtitle"],
        "professionalName": row["professional_name"],
        "footerText": row["footer_text"],
        "logoData": row["logo_data"],
        "theme": row["theme"],
    }


def require_object_payload() -> dict:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Envie os dados em formato JSON válido.")
    return payload


def validate_plan_payload(payload: dict) -> dict:
    title = str(payload.get("title", "")).strip()
    if not title:
        raise ValueError("Informe o nome do plano.")

    preferences = payload.get("preferences")
    targets = payload.get("targets")
    plan = payload.get("plan")

    if not isinstance(preferences, dict):
        raise ValueError("As preferências do plano são inválidas.")
    if not isinstance(targets, dict):
        raise ValueError("As metas do plano são inválidas.")
    if not isinstance(plan, list) or not plan:
        raise ValueError("O planejamento semanal está vazio.")

    return {
        "title": title[:180],
        "client_name": str(payload.get("clientName") or "Sem nome").strip()[:180] or "Sem nome",
        "preferences_json": json.dumps(preferences, ensure_ascii=False),
        "targets_json": json.dumps(targets, ensure_ascii=False),
        "plan_json": json.dumps(plan, ensure_ascii=False),
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "database": str(DATABASE_PATH.name)})


@app.get("/api/plans")
def list_plans():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM plans ORDER BY updated_at DESC"
        ).fetchall()
    return jsonify([plan_row_to_dict(row, include_plan=False) for row in rows])


@app.post("/api/plans")
def create_plan():
    try:
        payload = validate_plan_payload(require_object_payload())
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    plan_id = str(uuid.uuid4())
    now = utc_now()

    with get_db() as db:
        db.execute(
            """
            INSERT INTO plans (
                id, title, client_name, preferences_json,
                targets_json, plan_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan_id,
                payload["title"],
                payload["client_name"],
                payload["preferences_json"],
                payload["targets_json"],
                payload["plan_json"],
                now,
                now,
            ),
        )
        row = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()

    return jsonify(plan_row_to_dict(row)), 201


@app.get("/api/plans/<plan_id>")
def get_plan(plan_id: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Plano não encontrado."}), 404
    return jsonify(plan_row_to_dict(row))


@app.put("/api/plans/<plan_id>")
def update_plan(plan_id: str):
    try:
        payload = validate_plan_payload(require_object_payload())
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    now = utc_now()
    with get_db() as db:
        existing = db.execute("SELECT id FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if existing is None:
            return jsonify({"error": "Plano não encontrado."}), 404

        db.execute(
            """
            UPDATE plans
            SET title = ?, client_name = ?, preferences_json = ?,
                targets_json = ?, plan_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                payload["title"],
                payload["client_name"],
                payload["preferences_json"],
                payload["targets_json"],
                payload["plan_json"],
                now,
                plan_id,
            ),
        )
        row = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()

    return jsonify(plan_row_to_dict(row))


@app.delete("/api/plans/<plan_id>")
def delete_plan(plan_id: str):
    with get_db() as db:
        cursor = db.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Plano não encontrado."}), 404
    return jsonify({"deleted": True, "id": plan_id})


@app.post("/api/plans/<plan_id>/duplicate")
def duplicate_plan(plan_id: str):
    with get_db() as db:
        source = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if source is None:
            return jsonify({"error": "Plano não encontrado."}), 404

        new_id = str(uuid.uuid4())
        now = utc_now()
        db.execute(
            """
            INSERT INTO plans (
                id, title, client_name, preferences_json,
                targets_json, plan_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id,
                f"{source['title']} - Cópia",
                source["client_name"],
                source["preferences_json"],
                source["targets_json"],
                source["plan_json"],
                now,
                now,
            ),
        )
        row = db.execute("SELECT * FROM plans WHERE id = ?", (new_id,)).fetchone()

    return jsonify(plan_row_to_dict(row)), 201


@app.get("/api/settings")
def get_settings():
    with get_db() as db:
        row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()
    return jsonify(settings_row_to_dict(row))


@app.put("/api/settings")
def update_settings():
    try:
        payload = require_object_payload()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    settings = {
        "brandName": str(payload.get("brandName") or DEFAULT_SETTINGS["brandName"]).strip()[:120],
        "brandSubtitle": str(payload.get("brandSubtitle") or DEFAULT_SETTINGS["brandSubtitle"]).strip()[:180],
        "professionalName": str(payload.get("professionalName") or "").strip()[:180],
        "footerText": str(payload.get("footerText") or DEFAULT_SETTINGS["footerText"]).strip()[:600],
        "logoData": str(payload.get("logoData") or ""),
        "theme": str(payload.get("theme") or "teal"),
    }

    if settings["theme"] not in {"teal", "navy", "blue", "green", "graphite"}:
        settings["theme"] = "teal"
    if len(settings["logoData"]) > 6_000_000:
        return jsonify({"error": "O logotipo é muito grande."}), 400

    with get_db() as db:
        db.execute(
            """
            UPDATE settings
            SET brand_name = ?, brand_subtitle = ?, professional_name = ?,
                footer_text = ?, logo_data = ?, theme = ?, updated_at = ?
            WHERE id = 1
            """,
            (
                settings["brandName"],
                settings["brandSubtitle"],
                settings["professionalName"],
                settings["footerText"],
                settings["logoData"],
                settings["theme"],
                utc_now(),
            ),
        )
        row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()

    return jsonify(settings_row_to_dict(row))


@app.delete("/api/settings")
def reset_settings():
    with get_db() as db:
        db.execute(
            """
            UPDATE settings
            SET brand_name = ?, brand_subtitle = ?, professional_name = ?,
                footer_text = ?, logo_data = ?, theme = ?, updated_at = ?
            WHERE id = 1
            """,
            (
                DEFAULT_SETTINGS["brandName"],
                DEFAULT_SETTINGS["brandSubtitle"],
                DEFAULT_SETTINGS["professionalName"],
                DEFAULT_SETTINGS["footerText"],
                DEFAULT_SETTINGS["logoData"],
                DEFAULT_SETTINGS["theme"],
                utc_now(),
            ),
        )
        row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()
    return jsonify(settings_row_to_dict(row))


@app.get("/api/preferences")
def get_preferences():
    with get_db() as db:
        row = db.execute("SELECT data_json FROM preferences WHERE id = 1").fetchone()
    if row is None:
        return jsonify({})
    return jsonify(parse_json_text(row["data_json"], {}))


@app.put("/api/preferences")
def update_preferences():
    try:
        payload = require_object_payload()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    serialized = json.dumps(payload, ensure_ascii=False)
    with get_db() as db:
        db.execute(
            """
            INSERT INTO preferences (id, data_json, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                data_json = excluded.data_json,
                updated_at = excluded.updated_at
            """,
            (serialized, utc_now()),
        )
    return jsonify(payload)


@app.delete("/api/preferences")
def delete_preferences():
    with get_db() as db:
        db.execute("DELETE FROM preferences WHERE id = 1")
    return jsonify({"deleted": True})


@app.get("/api/export")
def export_database():
    with get_db() as db:
        plan_rows = db.execute("SELECT * FROM plans ORDER BY updated_at DESC").fetchall()
        settings_row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        preferences_row = db.execute("SELECT data_json FROM preferences WHERE id = 1").fetchone()

    export_data = {
        "exportedAt": utc_now(),
        "database": "SQLite",
        "settings": settings_row_to_dict(settings_row),
        "preferences": parse_json_text(preferences_row["data_json"], {}) if preferences_row else {},
        "plans": [plan_row_to_dict(row) for row in plan_rows],
    }

    content = json.dumps(export_data, ensure_ascii=False, indent=2)
    filename = f"backup-planos-{datetime.now().date().isoformat()}.json"
    return Response(
        content,
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "O arquivo enviado é muito grande."}), 413


@app.errorhandler(500)
def internal_error(error):
    app.logger.exception("Erro interno: %s", error)
    return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
