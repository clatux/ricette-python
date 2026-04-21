import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, session, abort, jsonify

app = Flask(__name__)
app.secret_key = "CAMBIA_QUESTA_PASSWORD"

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "ricette.json"


# ------------------------------
# Utility
# ------------------------------

def load_ricette():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ricette(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_categorie(ricette):
    return sorted({r["categoria"] for r in ricette})

def find_ricetta(ricette, id_ricetta):
    for r in ricette:
        if str(r["id"]) == str(id_ricetta):
            return r
    return None


# ------------------------------
# Rotte pubbliche
# ------------------------------

@app.route("/")
def home():
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    ultime = sorted(ricette, key=lambda r: r["id"], reverse=True)[:6]
    return render_template("index.html", ricette=ultime, categorie=categorie)


@app.route("/categoria/<nome>")
def categoria(nome):
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    filtrate = [r for r in ricette if r["categoria"] == nome]
    if not filtrate:
        abort(404)
    return render_template("categoria.html", categoria=nome, ricette=filtrate, categorie=categorie)


@app.route("/ricetta/<id_ricetta>")
def ricetta(id_ricetta):
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    r = find_ricetta(ricette, id_ricetta)
    if not r:
        abort(404)
    return render_template("ricetta.html", ricetta=r, categorie=categorie)


# ------------------------------
# Ricerca
# ------------------------------

@app.route("/search")
def search():
    q = request.args.get("q", "").lower()
    ricette = load_ricette()
    categorie = get_categorie(ricette)

    risultati = [
        r for r in ricette
        if q in r["titolo"].lower()
        or q in r["categoria"].lower()
        or q in r["ingredienti"].lower()
    ]

    return render_template("search.html", query=q, risultati=risultati, categorie=categorie)


# ------------------------------
# API
# ------------------------------

@app.route("/api/ricette")
def api_ricette():
    return jsonify(load_ricette())

@app.route("/api/ricetta/<id_ricetta>")
def api_ricetta(id_ricetta):
    r = find_ricetta(load_ricette(), id_ricetta)
    return jsonify(r or {"error": "not found"})

@app.route("/api/categorie")
def api_categorie():
    return jsonify(get_categorie(load_ricette()))

@app.route("/api/categoria/<nome>")
def api_categoria(nome):
    ricette = load_ricette()
    return jsonify([r for r in ricette if r["categoria"] == nome])

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").lower()
    ricette = load_ricette()
    risultati = [
        r for r in ricette
        if q in r["titolo"].lower()
        or q in r["categoria"].lower()
        or q in r["ingredienti"].lower()
    ]
    return jsonify(risultati)


# ------------------------------
# Admin
# ------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["password"] == "admin123":  # CAMBIA QUI
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    ricette = load_ricette()
    return render_template("admin_dashboard.html", ricette=ricette)


@app.route("/admin/nuova", methods=["GET", "POST"])
def admin_nuova():
    if "admin" not in session:
        return redirect("/admin/login")

    if request.method == "POST":
        ricette = load_ricette()
        nuova = {
            "id": max(r["id"] for r in ricette) + 1,
            "titolo": request.form["titolo"],
            "categoria": request.form["categoria"],
            "descrizione": request.form["descrizione"],
            "foto": request.form["foto"],
            "ingredienti": request.form["ingredienti"],
            "procedimento": request.form["procedimento"],
            "conservazione": request.form["conservazione"],
            "noteIngredienti": request.form["noteIngredienti"]
        }
        ricette.append(nuova)
        save_ricette(ricette)
        return redirect("/admin/dashboard")

    return render_template("admin_new.html")


@app.route("/admin/modifica/<id_ricetta>", methods=["GET", "POST"])
def admin_modifica(id_ricetta):
    if "admin" not in session:
        return redirect("/admin/login")

    ricette = load_ricette()
    r = find_ricetta(ricette, id_ricetta)

    if request.method == "POST":
        r["titolo"] = request.form["titolo"]
        r["categoria"] = request.form["categoria"]
        r["descrizione"] = request.form["descrizione"]
        r["foto"] = request.form["foto"]
        r["ingredienti"] = request.form["ingredienti"]
        r["procedimento"] = request.form["procedimento"]
        r["conservazione"] = request.form["conservazione"]
        r["noteIngredienti"] = request.form["noteIngredienti"]

        save_ricette(ricette)
        return redirect("/admin/dashboard")

    return render_template("admin_edit.html", ricetta=r)


@app.route("/admin/elimina/<id_ricetta>")
def admin_elimina(id_ricetta):
    if "admin" not in session:
        return redirect("/admin/login")

    ricette = load_ricette()
    ricette = [r for r in ricette if str(r["id"]) != str(id_ricetta)]
    save_ricette(ricette)
    return redirect("/admin/dashboard")
