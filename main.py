from flask import Flask, render_template, request, redirect, url_for
from db import db  # Stelle sicher, dass du die notwendigen Imports hast
from datetime import datetime
from flask_migrate import Migrate
from flask import render_template


app = Flask(__name__ , template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

class CD_METRIK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    code_change_volume = db.Column(db.Float, nullable=True)

@app.route("/")
def start_page():
    
    ccv_data = CD_METRIK.query.filter_by(name="Code Change Volume").all()
    return render_template('index.html', ccv_data=ccv_data)

@app.route("/submit_ccv", methods=["POST"])
def submit_ccv():
    ccv_value = request.form["ccvValue"]  # Die eingegebene Zahl aus dem Formular abrufen

    # Speichere ccv_value in der Datenbank, z.B. mit SQLAlchemy
    new_metric = CD_METRIK(name="Code Change Volume", code_change_volume=ccv_value)
    db.session.add(new_metric)
    db.session.commit()

    return redirect(url_for("start_page"))  # Nach dem Absenden zur Startseite weiterleiten

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/ccv_data", methods=["GET"])
def get_ccv_data():
    ccv_metrics = CD_METRIK.query.filter_by(name="Code Change Volume").all()
    return ccv_metrics
    
    