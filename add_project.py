from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)

class Projekt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True) # Optional

def add_project(name, description):
    with app.app_context():
        project = Projekt(name=name, description=description)
        db.session.add(project)
        db.session.commit()

if __name__ == "__main__":
    add_project("Zweites_Projekt", "Das zweite Projekt")
