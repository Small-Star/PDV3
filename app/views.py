from flask import render_template
from app import app, db
from app.models import Mood, QS_Params
import pandas as pd

import graph_mood, graph_diet, graph_body, graph_weightlifting

@app.route("/")
@app.route("/index")
def index():
    title = "Index"
    return render_template("index.html",title=title)

@app.route("/mood")
def mood():
    q = Mood.query.filter(Mood.date != None)
    data = pd.read_sql(q.statement, q.session.bind)
    script, div_days, div_avg_a, div_avg_v, div_good_days, div_poor_days, div_caution_days, div_warning_days, plot_ts_div, plot_vr_div, ma_slider_div = graph_mood.mood_graph(data)
    return render_template("mood.html",data=data, script=script, div_days=div_days, div_avg_a=div_avg_a, div_avg_v=div_avg_v, div_good_days=div_good_days, div_poor_days=div_poor_days, div_caution_days=div_caution_days, div_warning_days=div_warning_days, plot_ts_div=plot_ts_div, plot_vr_div=plot_vr_div, ma_slider_div=ma_slider_div, title="MOOD")

@app.route("/body")
def body():
    q = QS_Params.query.filter(QS_Params.kcal_intake >= 0) #Should include all the days
    data = pd.read_sql(q.statement, q.session.bind)
    script, div_days, div_avg_bg, div_avg_rhr, div_avg_slp_dur, div_avg_slp_q, div_days_bc, div_avg_wt, div_avg_bf, plot_blood_div, plot_rhr_div, plot_osq_div, plot_body_comp_div, plot_sleep_div, ma_slider_div = graph_body.body_graph(data)
    return render_template("body.html", data=data, script=script, div_days=div_days, div_avg_bg=div_avg_bg, div_avg_rhr=div_avg_rhr, div_avg_slp_dur=div_avg_slp_dur, div_avg_slp_q=div_avg_slp_q, div_days_bc=div_days_bc, div_avg_wt=div_avg_wt, div_avg_bf=div_avg_bf, plot_blood_div=plot_blood_div, plot_rhr_div=plot_rhr_div, plot_osq_div=plot_osq_div, plot_body_comp_div=plot_body_comp_div, plot_sleep_div=plot_sleep_div, ma_slider_div=ma_slider_div, title="BODY")

@app.route("/diet")
def diet():
    q = QS_Params.query.filter(QS_Params.kcal_intake >= 0)
    data = pd.read_sql(q.statement, q.session.bind)
    script, div_days, div_avg_intake, div_tdee, div_avg_net, div_avg_protein, div_avg_fat, div_avg_carb_all, div_avg_carb_net, div_avg_carb_fiber, div_problem_days, div_volatility, plot_comparison_div, plot_composition_div, ma_slider_div = graph_diet.diet_graph(data)
    return render_template("diet.html",data=data, script=script, div_days=div_days, div_avg_intake=div_avg_intake, div_tdee=div_tdee, div_avg_net=div_avg_net, div_avg_protein=div_avg_protein, div_avg_fat=div_avg_fat, div_avg_carb_all=div_avg_carb_all, div_avg_carb_net=div_avg_carb_net, div_avg_carb_fiber=div_avg_carb_fiber, div_problem_days=div_problem_days, div_volatility=div_volatility, plot_composition_div=plot_composition_div, plot_comparison_div=plot_comparison_div, ma_slider_div=ma_slider_div, title="DIET")

@app.route("/weightlifting")
def weightlifting():
    q = Lifts.query.filter(Lifts.date != None)
    data = pd.read_sql(q.statement, q.session.bind)
    script, plot_graph_div, plot_battleship_div, div_max, div_max_vol_per_set, div_total_volume = graph_weightlifting.weightlifting_graph(data)
    return render_template("weightlifting.html",data=data, plot_graph_div=plot_graph_div, plot_battleship_div=plot_battleship_div, div_max=div_max, div_max_vol_per_set=div_max_vol_per_set, div_total_volume=div_total_volume, title="WEIGHTLIFTING")

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
