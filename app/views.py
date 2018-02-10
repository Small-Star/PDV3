from flask import render_template
from app import app, db
from app.models import Mood, QS_Params
import pandas as pd

import graph_mood, graph_diet

@app.route("/")
@app.route("/index")
def index():
    title = "Index"
    return render_template("index.html",title=title)

@app.route("/mood")
def mood():
    q = Mood.query.filter(Mood.date != None)
    data = pd.read_sql(q.statement, q.session.bind)
    stats, script, plot_ts_div, plot_vr_div, ma_slider_div = graph_mood.mood_graph(data)
    return render_template("mood.html",data=data, script=script, plot_ts_div=plot_ts_div, plot_vr_div=plot_vr_div, ma_slider_div=ma_slider_div, stats=stats, title="MOOD")

@app.route("/body")
def body():
    title = "Body"
    return render_template("body.html",title=title)

@app.route("/diet")
def diet():
    q = QS_Params.query.filter(QS_Params.kcal_intake >= 0)
    data = pd.read_sql(q.statement, q.session.bind)
    stats, script, div, plot_comparison_div, plot_composition_div, ma_slider_div = graph_diet.diet_graph(data)
    return render_template("diet.html",data=data, script=script, div=div, plot_composition_div=plot_composition_div, plot_comparison_div=plot_comparison_div, ma_slider_div=ma_slider_div, stats=stats, title="DIET")

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
