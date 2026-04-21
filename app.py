from flask import Flask, render_template

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    ricette = [
        {"id": 1, "titolo": "Pasta al pomodoro", "categoria": "Primi"},
        {"id": 2, "titolo": "Tiramisù", "categoria": "Dolci"},
    ]
    return render_template("index.html", ricette=ricette)

# Pagina ricetta
@app.route("/ricetta/<int:id>")
def ricetta(id):
    ricetta = {
        "id": id,
        "titolo": "Pasta al pomodoro",
        "ingredienti": ["Pasta", "Pomodoro", "Sale", "Olio"],
        "preparazione": "Cuoci la pasta e aggiungi il sugo."
    }
    return render_template("ricetta.html", ricetta=ricetta)

if __name__ == "__main__":
    app.run(debug=True)
