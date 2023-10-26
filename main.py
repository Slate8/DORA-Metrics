"""
Dateiname: main.py
Autor: Tobias Trentzsch
Datum: 16. Oktober 2023
Beschreibung:
Im Rahmen meiner Bachelorarbeit entsteht hier das:

Continuous Delivery Monitoring-Tool (DORA)

Dieses Skript implementiert eine Webanwendung zur Überwachung von Continuous Delivery-Prozessen.
Es ermöglicht den Benutzern, verschiedene Arten von Metriken wie "Code Change Volume", "Lead Time for Changes" und "Mean Time To Recovery" zu erfassen.
Zusätzlich können Benutzer Vorfälle in Bezug auf Softwareentwicklungs- und Bereitstellungsprozesse melden. 
Die Daten werden in einer SQLite-Datenbank gespeichert, und die Anwendung bietet auch Benutzeranmeldefunktionen für erhöhte Sicherheit.

Hauptfunktionalitäten:
- Erfassen und Anzeigen von "Code Change Volume"-Daten
- Erfassen von Vorfällen und Berechnen der durchschnittlichen "Mean Time To Recovery"
- Erfassen und Anzeigen von "Lead Time for Changes"-Daten
- Benutzeranmelde- und Abmeldefunktion

Verwendete Technologien/Frameworks:
- Flask für das Web-Framework
- SQLite als Datenbank
- Flask-Migrate für Datenbankmigrationen
- Flask-Login für Benutzerverwaltung und -authentifizierung
Lizenz: MIT (oder jede andere Lizenz, die Sie verwenden möchten)
"""

# Hier beginnt der eigentliche Code...

from flask import Flask, jsonify, render_template, request, redirect, url_for
from db import db  # Stelle sicher, dass du die notwendigen Imports hast
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import extract
from models import User, CD_METRIK, Projekt, Incident, LTC


app = Flask(__name__, template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# muss noch angepasst werden
app.config['SECRET_KEY'] = 'dein_geheimer_schluessel'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@app.route("/")
def start_page():
    project_id = request.args.get('project_id', 'all')
    months, monthly_deployments = get_monthly_deployments(project_id)

    if project_id == 'all':
        mttr_data = calculate_mttr()  # Berechnet die MTTR für alle Projekte
        ccv_data = CD_METRIK.query.filter_by(name="Code Change Volume").all()
        ltc_data = LTC.query.filter_by(projekt_id=project_id).all()
        df_data = calculate_deployment_frequency()  # Berechnet die DF für alle Projekte

        # Zählen der fehlgeschlagenen Deployments
        failed_deployments = LTC.query.filter_by(
            deployment_successful=False).count()
        # Zählen  aller Deployments
        total_deployments = LTC.query.count()
    else:
        # Übergibt die Projekt-ID an Ihre calculate_mttr-Funktion
        mttr_data = calculate_mttr(project_id)
        ccv_data = CD_METRIK.query.filter_by(
            name="Code Change Volume", projekt_id=project_id).all()
        ltc_data = LTC.query.filter_by(projekt_id=project_id).all()
        # Berechnet die DF für das spezifische Projekt
        df_data = calculate_deployment_frequency(project_id)
        # Zählen Sie die fehlgeschlagenen Deployments für das spezifische Projekt
        failed_deployments = LTC.query.filter_by(
            deployment_successful=False, projekt_id=project_id).count()

        # Zählen Sie alle Deployments für das spezifische Projekt
        total_deployments = LTC.query.filter_by(projekt_id=project_id).count()

        # Berechnen Sie die CFR
    if total_deployments != 0:
        cfr = (failed_deployments / total_deployments) * 100
    else:
        cfr = 0

    projects = Projekt.query.all()

    return render_template('index.html', ccv_data=ccv_data, mttr=mttr_data, projects=projects,
                           ltc_data=ltc_data, current_project_id=project_id, df=df_data, months=months,
                           monthly_deployments=monthly_deployments, failed=failed_deployments,
                           total=total_deployments, cfr=cfr)


@app.route("/submit_ccv", methods=["POST"])
@login_required
def submit_ccv():
    # Die eingegebene Zahl aus dem Formular abrufen
    ccv_value = request.form["ccvValue"]
    selected_project_id = request.form["project_id"]

    # Überprüfen , ob selected_project_id "all" ist und behandeln  diesen Fall entsprechend (z. B. indem  ihn auf None setzen oder einen Fehler ausgeben)
    if selected_project_id == "all":
        selected_project_id = None

    # Speichere ccv_value und selected_project_id in der Datenbank
    new_metric = CD_METRIK(name="Code Change Volume", code_change_volume=ccv_value,
                           user_id=current_user.id, projekt_id=selected_project_id)
    db.session.add(new_metric)
    db.session.commit()

    # Nach dem Absenden zur Startseite weiterleiten
    return redirect(url_for("start_page"))


@app.route("/submit_mttr", methods=["POST"])
@login_required
def submit_mttr():
    # Die Daten aus dem Formular abrufen
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    # Konvertieren  die Zeichenketten in datetime-Objekte
    start_time_dt = datetime.fromisoformat(start_time)
    end_time_dt = datetime.fromisoformat(end_time)

    description = request.form["description"]
    cause = request.form["cause"]
    resolution = request.form["resolution"]
    selected_project_id = request.form["project_id"]

    # Die Daten in einem neuen Incident-Objekt speichern
    new_incident = Incident(start_time=start_time_dt,
                            end_time=end_time_dt,
                            description=description,
                            cause=cause,
                            resolution=resolution,
                            user_id=current_user.id,
                            projekt_id=selected_project_id)

    db.session.add(new_incident)
    db.session.commit()

    # Nach dem Absenden zur Startseite weiterleiten
    return redirect(url_for("start_page"))


@app.route("/submit_ltc", methods=["POST"])
@login_required
def submit_ltc():
    # Die eingegebenen Daten aus dem Formular abrufen
    commit_datetime = request.form["commit_datetime"]
    deployment_datetime = request.form["deployment_datetime"]
    selected_project_id = request.form["project_id"]
    deployment_status = True if request.form.get(
        "deployment_status") == "true" else False

    # Überprüfen , ob selected_project_id "all" ist
    if selected_project_id == "all":
        selected_project_id = None

    # Lead Time to Change berechnen
    commit_datetime_obj = datetime.fromisoformat(commit_datetime)
    deployment_datetime_obj = datetime.fromisoformat(deployment_datetime)
    ltc_value = (deployment_datetime_obj -
                 commit_datetime_obj).total_seconds() / 3600  # LTC in Stunden

    # Speichern  ltc_value, commit_datetime, deployment_datetime, deployment_status und selected_project_id in der Datenbank
    new_ltc = LTC(value=ltc_value,
                  commit_datetime=commit_datetime_obj,
                  deployment_datetime=deployment_datetime_obj, deployment_successful=deployment_status,
                  user_id=current_user.id,
                  projekt_id=selected_project_id)
    db.session.add(new_ltc)
    db.session.commit()

    # Nach dem Absenden zur Startseite weiterleiten
    return redirect(url_for("start_page"))


@app.route("/edit_ltc/<int:ltc_id>", methods=["GET"])
@login_required
def edit_ltc(ltc_id):
    # Holt den LTC-Eintrag aus der Datenbank
    ltc = LTC.query.get_or_404(ltc_id)

    # Stellt sicher, dass der aktuelle Benutzer berechtigt ist, diesen Eintrag zu bearbeiten
    if ltc.user_id != current_user.id:
        abort(403)  # Forbidden

    projects = Projekt.query.all()
    return render_template('edit_ltc.html', ltc=ltc, projects=projects)


@app.route("/update_ltc/<int:ltc_id>", methods=["POST"])
@login_required
def update_ltc(ltc_id):
    ltc = LTC.query.get_or_404(ltc_id)

    # Stellt wieder sicher, dass der aktuelle Benutzer berechtigt ist
    if ltc.user_id != current_user.id:
        abort(403)

    # Eingegebene Daten aus dem Formular holen
    commit_datetime = request.form["commit_datetime"]
    deployment_datetime = request.form["deployment_datetime"]
    deployment_status = request.form["deployment_status"]
    selected_project_id = request.form["project_id"]

    # Werte aktualisieren
    ltc.commit_datetime = datetime.fromisoformat(commit_datetime)
    ltc.deployment_datetime = datetime.fromisoformat(deployment_datetime)
    ltc.deployment_successful = True if deployment_status == "true" else False
    ltc.projekt_id = selected_project_id if selected_project_id != "all" else None

    # Lead Time to Change neu berechnen
    ltc_value = (ltc.deployment_datetime -
                 ltc.commit_datetime).total_seconds() / 3600  # LTC in Stunden
    ltc.value = ltc_value

    db.session.commit()

    # Nach dem Update zur Startseite oder einer anderen geeigneten Seite weiterleiten
    return redirect(url_for("start_page"))


@app.route("/calculate_mttr", methods=["GET"])
@login_required
def calculate_mttr(project_id=None):
    if project_id:
        # Hier berechnen  die MTTR nur für das spezifische Projekt
        incidents = Incident.query.filter_by(projekt_id=project_id).all()
    else:
        # Ansonsten berechnen  die MTTR für alle Projekte
        incidents = Incident.query.all()

    total_duration = 0

    for incident in incidents:
        duration = incident.end_time - incident.start_time
        total_duration += duration.total_seconds()  # Dauer in Sekunden

    if len(incidents) > 0:
        mttr_seconds = total_duration / len(incidents)
    else:
        mttr_seconds = 0

    # Konvertieren in Stunden:Minuten:Sekunden Format
    hours = mttr_seconds // 3600
    minutes = (mttr_seconds % 3600) // 60
    seconds = mttr_seconds % 60

    mttr_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    return mttr_str


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/get_ccv_data", methods=["GET"])
def get_ccv_data():
    project_id = request.args.get('projekt_id', 'all')

    if project_id == 'all':
        ccv_data = CD_METRIK.query.filter_by(name="Code Change Volume").all()
    else:
        ccv_data = CD_METRIK.query.filter_by(
            name="Code Change Volume", project_id=project_id).all()

    return ccv_data


# injeziert die Projekte in die Dropdownliste
@app.context_processor
def inject_projects():
    projects = Projekt.query.all()
    return dict(projects=projects)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("start_page"))
        else:
            error = "Benutzername oder Passwort ist nicht korrekt!"
    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


def calculate_deployment_frequency(project_id=None):
    if project_id and project_id != 'all':
        deployments = LTC.query.filter_by(projekt_id=project_id).count()
    else:
        # Zählt alle Deployments in der LTC-Tabelle
        deployments = LTC.query.count()

    return deployments


def get_monthly_deployments(project_id=None):
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]
    monthly_deployments = []

    for month in range(1, 13):  # Für jeden Monat des Jahres
        if project_id and project_id != 'all':
            count = LTC.query.filter(extract(
                'month', LTC.deployment_datetime) == month, LTC.projekt_id == project_id).count()
        else:
            count = LTC.query.filter(
                extract('month', LTC.deployment_datetime) == month).count()
        monthly_deployments.append(count)

    return months, monthly_deployments


if __name__ == "__main__":
    app.run(debug=True)
