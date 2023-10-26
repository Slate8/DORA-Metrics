from datetime import datetime
from db import db
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class CD_METRIK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    # muss noch gelöscht werden oder angepasst
    value = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    code_change_volume = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', name="fk_cd_metrik_user_id"))
    user = db.relationship('User')
    projekt_id = db.Column(db.Integer, db.ForeignKey(
        'projekt.id', name="fk_cd_metrik_projekt_id"))


class Projekt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)  # Optional
    metrics = db.relationship('CD_METRIK', backref='projekt')


class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    cause = db.Column(db.String(500), nullable=True)
    resolution = db.Column(db.String(500), nullable=True)
    projekt_id = db.Column(db.Integer, db.ForeignKey(
        'projekt.id', name="fk_incident_projekt_id"), nullable=False)
    projekt = db.relationship('Projekt', backref='incidents')
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', name="fk_incident_user_id"), nullable=False)
    user = db.relationship('User', backref='incidents')


class LTC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    commit_datetime = db.Column(db.DateTime, nullable=False)  # hinzugefügt
    deployment_datetime = db.Column(db.DateTime, nullable=False)  # hinzugefügt
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', name="fk_ltc_user_id"))
    user = db.relationship('User')
    projekt_id = db.Column(db.Integer, db.ForeignKey(
        'projekt.id', name="fk_ltc_projekt_id"))
    projekt = db.relationship('Projekt')
    deployment_successful = db.Column(db.Boolean, nullable=False, default=True)