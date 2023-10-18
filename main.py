from flask import Flask, render_template, request, redirect, url_for
from db import db  # Stelle sicher, dass du die notwendigen Imports hast
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__, template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dein_geheimer_schluessel'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class CD_METRIK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    code_change_volume = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', name="fk_user_id"))
    user = db.relationship('User')


@app.route("/")
def start_page():

    ccv_data = CD_METRIK.query.filter_by(name="Code Change Volume").all()
    return render_template('index.html', ccv_data=ccv_data)


@app.route("/submit_ccv", methods=["POST"])
@login_required
def submit_ccv():
    # Die eingegebene Zahl aus dem Formular abrufen
    ccv_value = request.form["ccvValue"]

    # Speichere ccv_value in der Datenbank, z.B. mit SQLAlchemy
    new_metric = CD_METRIK(name="Code Change Volume",
                           code_change_volume=ccv_value, user_id=current_user.id)
    db.session.add(new_metric)
    db.session.commit()

    # Nach dem Absenden zur Startseite weiterleiten
    return redirect(url_for("start_page"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/ccv_data", methods=["GET"])
def get_ccv_data():
    ccv_metrics = CD_METRIK.query.filter_by(name="Code Change Volume").all()
    return ccv_metrics


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


if __name__ == "__main__":
    app.run(debug=True)
