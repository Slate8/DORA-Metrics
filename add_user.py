from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

def add_user(username, password):
    with app.app_context():
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

if __name__ == "__main__":
    add_user("Tobi", "123")
