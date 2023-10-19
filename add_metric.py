from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)

class CD_METRIK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=True)  # muss noch gelöscht werden oder angepasst
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    code_change_volume = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_cd_metrik_user_id"))
    user = db.relationship('User')
    projekt_id = db.Column(db.Integer, db.ForeignKey('projekt.id', name="fk_cd_metrik_projekt_id"))
   # projekt = db.relationship('Projekt')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Projekt(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(200), unique=True, nullable=False)
   description = db.Column(db.String(500), nullable=True) # Optional
   metrics = db.relationship('CD_METRIK', backref='projekt')

def add_metric(name, value, code_change_volume, user_id, projekt_id):
    with app.app_context():
        user = User.query.get(user_id)
        projekt = Projekt.query.get(projekt_id)

        if not user or not projekt:
            print("User oder Projekt nicht gefunden.")
            return

        metric = CD_METRIK(name=name, value=value, code_change_volume=code_change_volume, user=user, projekt=projekt)
        db.session.add(metric)
        db.session.commit()
        print("Metrik erfolgreich hinzugefügt.")

if __name__ == "__main__":
    # Sie müssen die entsprechenden User- und Projekt-IDs bereitstellen.
    add_metric("CODE CHANGE VOLUME", 0, 100, 1, 1)