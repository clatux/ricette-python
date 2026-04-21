import json
from pathlib import Path
from flask import Flask, render_template, abort, jsonify

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "ricette.json"


def load_ricette():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_categorie(ricette):
    cats = sorted({r["categoria"] for r in ricette if r.get("categoria")})
    return cats


def find_ricetta(ricette, id_ricetta):
    for r in ricette:
        if str(r["id"]) == str(id_ricetta):
            return r
    return None


@app.route("/")
def home():
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    # ultime ricette: le ultime N per id
    ricette_ordinate = sorted(ricette, key=lambda r: r["id"], reverse=True)
    return render_template(
        "index.html",
        ricette=ricette_ordinate,
        categorie=categorie,
        titolo="Ricette della Casa"
    )


@app.route("/categoria/<nome>")
def categoria(nome):
    ricette = load_ricette()
    categorie = get_categorie(ricette)
    filtrate = [r for r in ricette if r.get("categoria") == nome]
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


# --- API per futura app Android ---

@app.route("/api/ricette")
def api_ricette():
    ricette = load_ricette()
    return jsonify(ricette)


@app.route("/api/ricetta/<id_ricetta>")
def api_ricetta(id_ricetta):
    ricette = load_ricette()
    r = find_ricetta(ricette, id_ricetta)
    if not r:
        return jsonify({"error": "not found"}), 404
    return jsonify(r)


@app.route("/api/categorie")
def api_categorie():
    ricette = load_ricette()
    return jsonify(get_categorie(ricette))


@app.route("/api/categoria/<nome>")
def api_categoria(nome):
    ricette = load_ricette()
    filtrate = [r for r in ricette if r.get("categoria") == nome]
    return jsonify(filtrate)


if __name__ == "__main__":
    app.run(debug=True)
