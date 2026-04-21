from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)

DATABASE = "ricette.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    db = get_db()
    ricette = db.execute("SELECT * FROM ricette ORDER BY id DESC").fetchall()
    return render_template("index.html", ricette=ricette)

@app.route("/ricetta/<int:id>")
def ricetta(id):
    db = get_db()
    ricetta = db.execute("SELECT * FROM ricette WHERE id = ?", (id,)).fetchone()
    return render_template("ricetta.html", ricetta=ricetta)

@app.route("/categoria/<nome>")
def categoria(nome):
    db = get_db()
    ricette = db.execute("SELECT * FROM ricette WHERE categoria = ?", (nome,)).fetchall()
    return render_template("categoria.html", categoria=nome, ricette=ricette)
