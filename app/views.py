#import sys
#sys.path.insert(0, './app')

from flask import render_template
from app import app

@app.route("/")
@app.route("/index")
def index():
    title = "Index"
    return render_template("index.html",title=title)

@app.route("/mood")
def mood():
    title = "Mood"
    return render_template("mood.html",title=title)

@app.route("/body")
def body():
    title = "Body"
    return render_template("body.html",title=title)

@app.route("/diet")
def diet():
    title = "Diet"
    return render_template("diet.html",title=title)

@app.route("/weightlifting")
def weightlifting():
    title = "Weightlifting"
    return render_template("weightlifting.html",title=title)

@app.route("/books")
def books():
    title = "Books"
    return render_template("books.html",title=title)

@app.route("/finances")
def finances():
    title = "finances"
    return render_template("finances.html",title=title)

@app.route("/dayviewer")
def dayviewer():
    title = "Dayviewer"
    return render_template("dayviewer.html",title=title)

@app.route("/settings")
def settings():
    title = "Settings"
    return render_template("settings.html",title=title)

@app.route("/update_db")
def update_db():
    title = "Update DB"
    return render_template("update_db.html",title=title)

@app.route("/rebuild_db")
def rebuild_db():
    title = "Rebuild DB"
    return render_template("rebuild_db.html",title=title)
