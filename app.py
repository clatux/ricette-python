import json
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect,
    session, abort, jsonify
)

app = Flask(__name__)
app.secret_key = "CAMBIA_QUESTA_PASSWORD"  # cambia questa stringa

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
    """
    Restituisce le categorie in ordine personalizzato,
    senza duplicati, senza spazi, con maiuscola corretta.
    """

    ordine = [
        "Primi",
        "Secondi",
        "Contorni",
        "Dolci",
        "Lievitazioni",
        "Pane",
        "Antipasti",
        "Pizze",
        "Torte",
    ]

    trovate = set()

    for r in ricette:
        cat = r.get("categoria", "").strip().capitalize()
        if cat:
            trovate.add(cat)

    # categorie nell'ordine desiderato
    ordinate = [c for c in ordine if c in trovate]

    # categorie non previste → in fondo
    extra = [c for c in trovate if c not in ordine]

    return ordinate + extra


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
    return render_template(
        "index.html",
        ricette=ultime,
        categorie=categorie,
        titolo="Ricette della Casa"
    )


@app.route("/categoria/<nome>")
def categoria(nome):
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    filtrate = [r for r in ricette if r.get("categoria").strip().capitalize() == nome]
    if not filtrate:
        abort(404)
    return render_template(
        "categoria.html",
        categoria=nome,
        ricette=filtrate,
        categorie=categorie,
        titolo=f"{nome} - Ricette della Casa"
    )


@app.route("/ricetta/<id_ricetta>")
def ricetta(id_ricetta):
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    r = find_ricetta(ricette, id_ricetta)
    if not r:
        abort(404)
    return render_template(
        "ricetta.html",
        ricetta=r,
        categorie=categorie,
        titolo=f"{r['titolo']} - Ricette della Casa"
    )


# ------------------------------
# Ricerca
# ------------------------------

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    ricette = load_ricette()
    categorie = get_categorie(ricette)

    if not q:
        return render_template(
            "search.html",
            query=q,
            risultati=[],
            categorie=categorie,
            titolo="Cerca - Ricette della Casa"
        )

    q_low = q.lower()
    risultati = [
        r for r in ricette
        if q_low in r["titolo"].lower()
        or q_low in r["categoria"].lower()
        or q_low in r["ingredienti"].lower()
    ]

    return render_template(
        "search.html",
        query=q,
        risultati=risultati,
        categorie=categorie,
        titolo=f"Risultati per {q} - Ricette della Casa"
    )


# ------------------------------
# API
# ------------------------------

@app.route("/api/ricette")
def api_ricette():
    return jsonify(load_ricette())


@app.route("/api/ricetta/<id_ricetta>")
def api_ricetta(id_ricetta):
    r = find_ricetta(load_ricette(), id_ricetta)
    if not r:
        return jsonify({"error": "not found"}), 404
    return jsonify(r)


@app.route("/api/categorie")
def api_categorie():
    return jsonify(get_categorie(load_ricette()))


@app.route("/api/categoria/<nome>")
def api_categoria(nome):
    ricette = load_ricette()
    filtrate = [
        r for r in ricette
        if r.get("categoria", "").strip().capitalize() == nome
    ]
    return jsonify(filtrate)


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
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
        password = request.form.get("password", "")
        if password == "admin123":  # CAMBIA QUI
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html", titolo="Login admin")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    ricette = load_ricette()
    return render_template(
        "admin_dashboard.html",
        ricette=ricette,
        categorie=get_categorie(ricette),
        titolo="Admin - Dashboard"
    )


@app.route("/admin/nuova", methods=["GET", "POST"])
def admin_nuova():
    if "admin" not in session:
        return redirect("/admin/login")

    if request.method == "POST":
        ricette = load_ricette()
        nuovo_id = max(r["id"] for r in ricette) + 1 if ricette else 1

        nuova = {
            "id": nuovo_id,
            "titolo": request.form.get("titolo", "").strip(),
            "categoria": request.form.get("categoria", "").strip().capitalize(),
            "descrizione": request.form.get("descrizione", "").strip(),
            "foto": request.form.get("foto", "").strip(),
            "ingredienti": request.form.get("ingredienti", "").strip(),
            "procedimento": request.form.get("procedimento", "").strip(),
            "conservazione": request.form.get("conservazione", "").strip(),
            "noteIngredienti": request.form.get("noteIngredienti", "").strip()
        }

        ricette.append(nuova)
        save_ricette(ricette)
        return redirect("/admin/dashboard")

    return render_template("admin_new.html", titolo="Nuova ricetta")


@app.route("/admin/modifica/<id_ricetta>", methods=["GET", "POST"])
def admin_modifica(id_ricetta):
    if "admin" not in session:
        return redirect("/admin/login")

    ricette = load_ricette()
    r = find_ricetta(ricette, id_ricetta)
    if not r:
        abort(404)

    if request.method == "POST":
        r["titolo"] = request.form.get("titolo", "").strip()
        r["categoria"] = request.form.get("categoria", "").strip().capitalize()
        r["descrizione"] = request.form.get("descrizione", "").strip()
        r["foto"] = request.form.get("foto", "").strip()
        r["ingredienti"] = request.form.get("ingredienti", "").strip()
        r["procedimento"] = request.form.get("procedimento", "").strip()
        r["conservazione"] = request.form.get("conservazione", "").strip()
        r["noteIngredienti"] = request.form.get("noteIngredienti", "").strip()

        save_ricette(ricette)
        return redirect("/admin/dashboard")

    return render_template(
        "admin_edit.html",
        ricetta=r,
        categorie=get_categorie(ricette),
        titolo=f"Modifica - {r['titolo']}"
    )


@app.route("/admin/elimina/<id_ricetta>")
def admin_elimina(id_ricetta):
    if "admin" not in session:
        return redirect("/admin/login")

    ricette = load_ricette()
    ricette = [r for r in ricette if str(r["id"]) != str(id_ricetta)]
    save_ricette(ricette)
    return redirect("/admin/dashboard")


if __name__ == "__main__":
    app.run(debug=True)
