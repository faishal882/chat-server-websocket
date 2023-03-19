from flask import Flask, render_template, url_for, redirect, session, request, flash
from client.client import Client
import time
from threading import Thread
from models import DataBase

app = Flask(__name__)
app.secret_key = "hello1234"

NAME_KEY = "name"
client = None
messages = []


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":  # if user input a name
        name = request.form["inputName"]
        if len(name) >= 2:
            session[NAME_KEY] = name
            flash(f'You were successfully logged in as {name}.')
            return redirect(url_for("home"))
        else:
            flash("1Name must be longer than 1 character.")

    return render_template("login.html",  **{"session": session})


@app.route("/logout")
def logout():
    session.pop(NAME_KEY, None)
    flash("0You were logged out.")
    return redirect(url_for("login"))


@app.route("/")
@app.route("/home")
def home():
    global client
    if NAME_KEY not in session:
        return redirect(url_for("login"))

    client = Client(session[NAME_KEY])
    return render_template("index.html", **{"session": session})


@app.route('/run', methods=["GET"])
def run(url=None):
    global client
    global messages
    msg = request.args.get('msg')
    if client != None:
        client.send_message(msg)
        if msg != "":
            db = DataBase()
            db.save_message(session[NAME_KEY], msg)
        return render_template("index.html", **{"session": session, "messages": messages})
    else:
        return render_template("index.html", **{"session": session})


def update_messages():
    global client
    global messages
    while True:
        if client != None:
            time.sleep(0.1)
            new_messages = client.get_messages()
            messages.extend(new_messages)


if __name__ == "__main__":
    Thread(target=update_messages).start()
    app.run(debug=True)
