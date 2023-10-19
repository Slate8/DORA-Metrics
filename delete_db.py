from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class CD_METRIK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=True)  # muss noch gelöscht werden oder angepasst
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    code_change_volume = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_cd_metrik_user_id"))
    user = db.relationship('User')
    projekt_id = db.Column(db.Integer, db.ForeignKey('projekt.id', name="fk_cd_metrik_projekt_id"))
    projekt = db.relationship('Projekt')

class Projekt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True) # Optional

def delete_cd_metrik_data():
    with app.app_context():
        CD_METRIK.query.delete()
        db.session.commit()

if __name__ == "__main__":
    delete_cd_metrik_data()
