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
# Import der benötigten Module und Bibliotheken
from flask import Flask, jsonify, render_template, request, redirect, url_for
from db import db  
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, login_required,  current_user
from sqlalchemy import extract
from models import User, CD_METRIK, Projekt, Incident, LTC
from sqlalchemy.orm import joinedload
from flask import session
from views.auth import auth
from flask_login import current_user
import os
from dotenv import load_dotenv
load_dotenv()
from flask import abort


# Initialisierung der Flask-Anwendung und Konfiguration
app = Flask(__name__, template_folder="templates")
app.register_blueprint(auth, url_prefix='/auth')

# Konfiguration der Datenbank und anderer Flask-Erweiterungen
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.init_app(app)

# Deklaration der Route für die Startseite, erfordert Login
@app.route("/")
@login_required
def start_page():
     # Logik zur Abfrage und Anzeige der Startseite-Daten
    project_id = request.args.get('project_id', 'all')
    months, monthly_deployments = get_monthly_deployments(project_id)
      # Holen  den Benutzernamen aus der Session
    username = current_user.username if current_user.is_authenticated else 'Unbekannter Benutzer'


    if project_id == 'all':
        mttr_data = calculate_mttr()  # Berechnet die MTTR für alle Projekte
        ccv_data = CD_METRIK.query.filter_by(name="Code Change Volume").all()
        ltc_data = LTC.query.filter_by(projekt_id=project_id).all()
        df_data = calculate_deployment_frequency()  # Berechnet die DF für alle Projekte
        incident_data = Incident.query.all()
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
        # Zählen der fehlgeschlagenen Deployments für das spezifische Projekt
        failed_deployments = LTC.query.filter_by(
            deployment_successful=False, projekt_id=project_id).count()

        # Zählen Sie alle Deployments für das spezifische Projekt
        total_deployments = LTC.query.filter_by(projekt_id=project_id).count()
        incident_data = Incident.query.filter_by(projekt_id=project_id).all()

        # Berechnen der CFR im html
    if total_deployments != 0:
        cfr = (failed_deployments / total_deployments) * 100
    else:
        cfr = 0

    projects = Projekt.query.all()

    return render_template('index.html',username=username, ccv_data=ccv_data, mttr=mttr_data, projects=projects,
                           ltc_data=ltc_data, current_project_id=project_id, df=df_data, months=months,
                           monthly_deployments=monthly_deployments, failed=failed_deployments,
                           total=total_deployments, cfr=cfr, incident_data=incident_data)


# AJAX-Route zur Abfrage der Tabelle "CD-Metrik"
@app.route('/get_cd_metric_data')
def get_cd_metric_data():
    project_id = request.args.get('project_id', 'all')
    if project_id == 'all':
        metrics_data = CD_METRIK.query.options(
            joinedload(CD_METRIK.user)).all()
    else:
        metrics_data = CD_METRIK.query.options(joinedload(
            CD_METRIK.user)).filter_by(projekt_id=project_id).all()

    # Konvertieren der Daten in ein serialisierbares Format
    metrics_data_list = [
        {
            'id': metric.id,
            'name': metric.name,
            'value': metric.value,
           # 'timestamp': metric.timestamp.strftime('%H:%M %d.%m.%Y')if metric.timestamp else 'N/A',
            'commit_datetime': metric.commit_datetime.strftime('%H:%M %d.%m.%Y') if metric.commit_datetime else 'N/A',
            'code_change_volume': metric.code_change_volume,
            'user_id': metric.user_id,
            'user': metric.user.username,
            'projekt_id': metric.projekt_id,
            'projekt': metric.projekt.name if metric.projekt else None
        }
        for metric in metrics_data
    ]

    return jsonify(metrics_data_list)

# Route zur Abfrage von LTC-Daten
@app.route('/get_ltc_data')
def get_ltc_data():
    project_id = request.args.get('project_id', 'all')
    if project_id == 'all':
        ltc_data = LTC.query.all()
    else:
        ltc_data = LTC.query.filter_by(projekt_id=project_id).all()

    # Konvertieren der Daten in ein serialisierbares Format
    ltc_data_list = [
        {
            'id': data.id,
            'ltc_value': f'{data.value:.2f}',
            'commit': data.commit_datetime.strftime('%H:%M %d.%m.%Y'),
            'deploy': data.deployment_datetime.strftime('%H:%M %d.%m.%Y'),
            'user': data.user.username,
            'deploy_successful': str(data.deployment_successful)
        }
        for data in ltc_data
    ]

    return jsonify(ltc_data_list)

# Route zur Abfrage von MTTR-Daten
@app.route('/get_mttr_data')
def get_mttr_data():
    project_id = request.args.get('project_id', 'all')
    if project_id == 'all':
        incidents = Incident.query.all()
    else:
        incidents = Incident.query.filter_by(projekt_id=project_id).all()

   # Hier beginnt die MTTR-Berechnung
    total_duration = sum(
        (incident.end_time - incident.start_time).total_seconds() for incident in incidents)
    mttr_seconds = total_duration / len(incidents) if incidents else 0

    # Konvertieren in Stunden:Minuten:Sekunden Format
    hours = mttr_seconds // 3600
    minutes = (mttr_seconds % 3600) // 60
    seconds = mttr_seconds % 60

    mttr_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    # Hier endet die MTTR-Berechnung

    # Konvertieren der Daten in ein serialisierbares Format
    mttr_data_list = [
        {
            'id': incident.id,
            'starttime': incident.start_time.strftime('%H:%M %d.%m.%Y'),
            'endtime': incident.end_time.strftime('%H:%M %d.%m.%Y'),
            'description': incident.description,
            'project': incident.projekt.name
        }
        for incident in incidents
    ]

    # MTTR in das Antwortobjekt aufnehmen
    response = {
        'mttr': mttr_str,
        'data': mttr_data_list
    }

    return jsonify(response)

# Route zur Abfrage und Berechnung der CFR-Daten
@app.route('/get_cfr_data')
def get_cfr_data():
    project_id = request.args.get('project_id', 'all')
    if project_id == 'all':
        failed_deployments = LTC.query.filter_by(
            deployment_successful=False).count()
        total_deployments = LTC.query.count()
    else:
        failed_deployments = LTC.query.filter_by(
            deployment_successful=False, projekt_id=project_id).count()
        total_deployments = LTC.query.filter_by(projekt_id=project_id).count()

    if total_deployments != 0:
        cfr = (failed_deployments / total_deployments) * 100
    else:
        cfr = 0

    return jsonify({'cfr': cfr, 'failed': failed_deployments, 'total': total_deployments})


# Route zur Abfrage und Berechnung der DF-Daten
@app.route('/get_df_data')
def get_df_data():
    project_id = request.args.get('project_id', 'all')
    df_data = calculate_deployment_frequency(project_id)
    months, monthly_deployments = get_monthly_deployments(project_id)
    return jsonify(df=df_data, months=months, deployments=monthly_deployments)

# Route zur Verarbeitung des CCV-Formulars
@app.route("/submit_ccv", methods=["POST"])
@login_required
def submit_ccv():
    # Die eingegebene Zahl aus dem Formular abrufen
    ccv_value = request.form["ccvValue"]
    selected_project_id = request.form["project_id"]
    commit_datetime_str = request.form.get("commit_ccv_datetime")
    commit_datetime = datetime.strptime(commit_datetime_str, "%Y-%m-%dT%H:%M")


    # Überprüfen , ob selected_project_id "all" ist und behandeln  diesen Fall entsprechend (z. B. indem  ihn auf None setzen oder einen Fehler ausgeben)
    if selected_project_id == "all":
        selected_project_id = None

    # Speichere ccv_value und selected_project_id in der Datenbank
    new_metric = CD_METRIK(
        name="Code Change Volume",
        code_change_volume=ccv_value,
        user_id=current_user.id,
        projekt_id=selected_project_id,
        commit_datetime=commit_datetime  # Setze das übergebene Datum und Zeit
    )
    db.session.add(new_metric)
    db.session.commit()

    # Nach dem Absenden zur Startseite weiterleiten
    return redirect(url_for("start_page"))

# Route zur Verarbeitung des MTTR-Formulars
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

# Route zur Verarbeitung des LTC-Formulars
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
   # Ruft den LTC-Eintrag anhand der übergebenen ID aus der Datenbank ab und gibt einen 404-Fehler zurück, falls nicht vorhanden
    ltc = LTC.query.get_or_404(ltc_id)

   # Prüft, ob der aktuelle Benutzer berechtigt ist, diesen Eintrag zu bearbeiten. Gibt im Fehlerfall einen 403-Fehler zurück
  #  if ltc.user_id != current_user.id:
  #      abort(403)  # Zugriff verboten

    # Ruft alle Projekte aus der Datenbank ab
    projects = Projekt.query.all()
    # Rendert das 'edit_ltc.html'-Template, übergibt die LTC-Instanz und die Projektliste
    return render_template('edit_ltc.html', ltc=ltc, projects=projects)


@app.route("/update_ltc/<int:ltc_id>", methods=["POST"])
@login_required
def update_ltc(ltc_id):
     # Ähnlich wie bei 'edit_ltc', aber hier werden die aktualisierten Daten verarbeitet
    ltc = LTC.query.get_or_404(ltc_id)

    # Stellt wieder sicher, dass der aktuelle Benutzer berechtigt ist
   # if ltc.user_id != current_user.id:
   #     abort(403)

    # Eingegebene Daten aus dem Formular holen
    commit_datetime = request.form["commit_datetime"]
    deployment_datetime = request.form["deployment_datetime"]
    deployment_status = request.form["deployment_status"]
    selected_project_id = request.form["project_id"]

    # Aktualisiert den LTC-Eintrag mit den neuen Daten
    ltc.commit_datetime = datetime.fromisoformat(commit_datetime)
    ltc.deployment_datetime = datetime.fromisoformat(deployment_datetime)
    ltc.deployment_successful = True if deployment_status == "true" else False
    ltc.projekt_id = selected_project_id if selected_project_id != "all" else None

    # Berechnet den neuen LTC-Wert und speichert die Änderungen in der Datenbank
    ltc_value = (ltc.deployment_datetime -
                 ltc.commit_datetime).total_seconds() / 3600  # LTC in Stunden
    ltc.value = ltc_value

    db.session.commit()

    # Nach dem Update zur Startseite oder einer anderen geeigneten Seite weiterleiten
    return redirect(url_for("start_page"))

@app.route("/edit_ccv/<int:ccv_id>", methods=["GET"])
@login_required
def edit_ccv(ccv_id):
    # Holt den LTC-Eintrag aus der Datenbank
    metric = CD_METRIK.query.get_or_404(ccv_id)

    # Stellt sicher, dass der aktuelle Benutzer berechtigt ist, diesen Eintrag zu bearbeiten
   ## if metric.user_id != current_user.id:
   ##     abort(403)  # Forbidden

    projects = Projekt.query.all()
    return render_template('edit_ccv.html', metric=metric, projects=projects)


@app.route('/update_ccv/<int:ccv_id>', methods=['POST'])
@login_required
def update_ccv(ccv_id):
    metric = CD_METRIK.query.get_or_404(ccv_id)

  ##  if metric.user_id != current_user.id:
   ##     abort(403)

    metric.timestamp = datetime.fromisoformat(request.form['timestamp'])
    metric.code_change_volume = request.form['ccvValue']
    # Aktualisieren Sie hier weitere Felder wie Benutzer- und Projektinformationen, falls nötig

    db.session.commit()
    return redirect(url_for('start_page'))

@app.route("/edit_mttr/<int:incident_id>", methods=["GET"])
@login_required
def edit_mttr(incident_id):
    # Holt den Incident-Eintrag anhand der übergebenen ID aus der Datenbank
    incident = Incident.query.get_or_404(incident_id)

    # Prüft, ob der aktuelle Benutzer berechtigt ist, diesen Eintrag zu bearbeiten
    if incident.user_id != current_user.id:
        abort(403)  # Forbidden

    # Rendert das 'edit_mttr.html'-Template, übergibt die Incident-Instanz
    return render_template('edit_mttr.html', incident=incident)

@app.route("/update_mttr/<int:incident_id>", methods=["POST"])
@login_required
def update_mttr(incident_id):
    # Holt den Incident-Eintrag anhand der übergebenen ID aus der Datenbank
    incident = Incident.query.get_or_404(incident_id)

    # Prüft, ob der aktuelle Benutzer berechtigt ist, diesen Eintrag zu bearbeiten
    if incident.user_id != current_user.id:
        abort(403)  # Forbidden

    # Die Daten aus dem Formular abrufen
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    description = request.form["description"]
    cause = request.form["cause"]
    resolution = request.form["resolution"]
    selected_project_id = request.form["project_id"]

    # Konvertieren die Zeichenketten in datetime-Objekte
    start_time_dt = datetime.fromisoformat(start_time)
    end_time_dt = datetime.fromisoformat(end_time)

    # Aktualisiert das Incident-Objekt
    incident.start_time = start_time_dt
    incident.end_time = end_time_dt
    incident.description = description
    incident.cause = cause
    incident.resolution = resolution
    incident.projekt_id = selected_project_id if selected_project_id != "all" else None

    # Speichert die Änderungen in der Datenbank
    db.session.commit()

    # Nach dem Update zur Startseite oder einer anderen geeigneten Seite weiterleiten
    return redirect(url_for("start_page"))




@app.route("/calculate_mttr", methods=["GET"])
@login_required
def calculate_mttr(project_id=None):
    # Berechnet die Mean Time To Recovery (MTTR) für ein spezifisches Projekt oder alle Projekte
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
    # Lädt einen Benutzer anhand seiner ID aus der Datenbank für die Authentifizierung
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
      # Stellt eine Liste aller Projekte für die Verwendung in Templates bereit
    projects = Projekt.query.all()
    return dict(projects=projects)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def calculate_deployment_frequency(project_id=None):
   # Berechnet die Deployment-Frequenz für ein bestimmtes Projekt oder alle Projekte
    # Initialisiere die Anzahl der aktiven Monate
    active_months = 0
    total_deployments = 0

    for month in range(1, 13):  # Für jeden Monat des Jahres
        if project_id and project_id != 'all':
            # Zählt die Deployments für den gegebenen Monat und das spezifische Projekt
            monthly_deployments = LTC.query.filter(
                extract('month', LTC.deployment_datetime) == month,
                LTC.projekt_id == project_id
            ).count()
        else:
            # Zählt die Deployments für den gegebenen Monat über alle Projekte
            monthly_deployments = LTC.query.filter(
                extract('month', LTC.deployment_datetime) == month
            ).count()

        # Wenn in dem Monat Deployments stattgefunden haben, erhöhe die Zähler
        if monthly_deployments > 0:
            active_months += 1
            total_deployments += monthly_deployments

    # Berechnung der Deployment-Frequenz
    if active_months > 0:  # Vermeidung der Division durch Null
        deployment_frequency = total_deployments / active_months
    else:
        deployment_frequency = 0

    return deployment_frequency

# Funktion für die Darstellung im DF-Chart


def get_monthly_deployments(project_id=None):
      # Holt die monatlichen Deployments für ein bestimmtes Projekt oder alle Projekte
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


@app.route('/create_project', methods=['POST'])
def create_project():
# Erstellt ein neues Projekt basierend auf den Formulardaten

    name = request.form['name']
    description = request.form.get('description', '')

    existing_project = Projekt.query.filter_by(name=name).first()
    if existing_project:
        return jsonify({'success': False, 'message': 'Ein Projekt mit diesem Namen existiert bereits.'}), 400

    try:
        with app.app_context():
            project = Projekt(name=name, description=description)
            db.session.add(project)
            db.session.commit()
        return jsonify({'success': True, 'message': 'Projekt erfolgreich erstellt!'})

    except Exception as e:
        app.logger.error(f'Fehler beim Erstellen des Projekts: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# Hauptfunktion zum Starten der Flask-Anwendung
if __name__ == "__main__":
    app.run(debug=True)
