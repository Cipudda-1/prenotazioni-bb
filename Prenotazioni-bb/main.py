from datetime import datetime
import random
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Database temporaneo in memoria (in un progetto reale userai SQLite o PostgreSQL)
# Struttura: { "PIN": {"telefono": "...", "inizio": "...", "fine": "..."} }
prenotazioni_db = {}


@app.route("/")
def home():
  return render_template("index.html")


# API per aggiungere una prenotazione dal sito
@app.route("/api/prenota", methods=["POST"])
def prenota():
  dati = request.json
  telefono = dati.get("telefono")
  inizio = dati.get("inizio")  # Formato "YYYY-MM-DD"
  fine = dati.get("fine")  # Formato "YYYY-MM-DD"

  # Genera un PIN univoco a 4 cifre
  pin = str(random.randint(1000, 9999))
  while pin in prenotazioni_db:
    pin = str(random.randint(1000, 9999))

  prenotazioni_db[pin] = {"telefono": telefono, "inizio": inizio, "fine": fine}

  return jsonify({"success": True, "pin": pin})


# API che l'ESP32 interroga per scaricare i PIN attivi oggi
@app.route("/api/active-pins", methods=["GET"])
def get_active_pins():
  oggi_str = datetime.now().strftime("%Y-%m-%d")
  oggi_date = datetime.strptime(oggi_str, "%Y-%m-%d")

  pins_attivi = []

  for pin, info in prenotazioni_db.items():
    d_inizio = datetime.strptime(info["inizio"], "%Y-%m-%d")
    d_fine = datetime.strptime(info["fine"], "%Y-%m-%d")

    # Controlla se oggi la prenotazione è attiva
    if d_inizio <= oggi_date <= d_fine:
      pins_attivi.append(pin)

  return jsonify({"active_pins": pins_attivi})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)