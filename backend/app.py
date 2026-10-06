import os

import psycopg
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=os.environ.get("CORS_ORIGIN", "*"))


def initialize_database():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return
    try:
        with psycopg.connect(database_url) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id serial primary key,
                    title text not null,
                    done boolean not null default false
                )
                """
            )
    except psycopg.Error:
        pass


def database_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None
    return psycopg.connect(database_url)


def database_not_configured():
    return jsonify(error="database not configured"), 503


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/todos")
def list_todos():
    connection = database_connection()
    if connection is None:
        return database_not_configured()
    with connection:
        rows = connection.execute(
            "SELECT id, title, done FROM todos ORDER BY id"
        ).fetchall()
    return jsonify([{"id": row[0], "title": row[1], "done": row[2]} for row in rows])


@app.post("/todos")
def create_todo():
    connection = database_connection()
    if connection is None:
        return database_not_configured()
    data = request.get_json(silent=True)
    title = data.get("title") if isinstance(data, dict) else None
    if not isinstance(title, str) or not title.strip():
        return jsonify(error="title must be a non-empty string"), 400
    with connection:
        row = connection.execute(
            "INSERT INTO todos (title) VALUES (%s) RETURNING id, title, done",
            (title.strip(),),
        ).fetchone()
    return jsonify({"id": row[0], "title": row[1], "done": row[2]}), 201


@app.patch("/todos/<int:todo_id>")
def update_todo(todo_id):
    connection = database_connection()
    if connection is None:
        return database_not_configured()
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify(error="provide title or done"), 400
    updates = []
    values = []
    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify(error="title must be a non-empty string"), 400
        updates.append("title = %s")
        values.append(data["title"].strip())
    if "done" in data:
        if not isinstance(data["done"], bool):
            return jsonify(error="done must be a boolean"), 400
        updates.append("done = %s")
        values.append(data["done"])
    if not updates:
        return jsonify(error="provide title or done"), 400
    values.append(todo_id)
    with connection:
        row = connection.execute(
            f"UPDATE todos SET {', '.join(updates)} WHERE id = %s "
            "RETURNING id, title, done",
            values,
        ).fetchone()
    if row is None:
        return jsonify(error="todo not found"), 404
    return jsonify({"id": row[0], "title": row[1], "done": row[2]})


@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    connection = database_connection()
    if connection is None:
        return database_not_configured()
    with connection:
        row = connection.execute(
            "DELETE FROM todos WHERE id = %s RETURNING id", (todo_id,)
        ).fetchone()
    if row is None:
        return jsonify(error="todo not found"), 404
    return "", 204


initialize_database()
