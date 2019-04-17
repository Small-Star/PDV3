from flask import render_template
from app import app, db
from app.models import Mood, QS_Params, Lifts
import pandas as pd

import graph_mood, graph_diet, graph_body, graph_weightlifting, graph_meditation, analysis

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
    script, div_stairs, div_num_ohp, div_workouts, div_wilks, div_squat_max, div_deadlift_max, div_bench_max, div_ohp_max, div_squat_max_vol_per_set, div_deadlift_max_vol_per_set, div_bench_max_vol_per_set, div_ohp_max_vol_per_set, div_squat_total_vol, div_deadlift_total_vol, div_bench_total_vol, div_ohp_total_vol, plot_max_div, plot_mvps_div, plot_tv_div, ma_slider_div = graph_weightlifting.weightlifting_graph(data)
    return render_template("weightlifting.html",data=data, script=script, div_stairs=div_stairs, div_num_ohp=div_num_ohp, div_workouts=div_workouts, div_wilks=div_wilks, div_squat_max=div_squat_max, div_deadlift_max=div_deadlift_max, div_bench_max=div_bench_max, div_ohp_max=div_ohp_max, div_squat_max_vol_per_set=div_squat_max_vol_per_set, div_deadlift_max_vol_per_set=div_deadlift_max_vol_per_set, div_bench_max_vol_per_set=div_bench_max_vol_per_set, div_ohp_max_vol_per_set=div_ohp_max_vol_per_set, div_squat_total_vol=div_squat_total_vol, div_deadlift_total_vol=div_deadlift_total_vol, div_bench_total_vol=div_bench_total_vol, div_ohp_total_vol=div_ohp_total_vol,  plot_max_div=plot_max_div, plot_mvps_div=plot_mvps_div, plot_tv_div=plot_tv_div, ma_slider_div=ma_slider_div, title="WEIGHTLIFTING")

@app.route("/meditation")
def meditation():
    q = QS_Params.query.filter(QS_Params.meditation_time >= 0).order_by(QS_Params.date)
    data = pd.read_sql(q.statement, q.session.bind)
    script, plot_daily_div, plot_cumu_div = graph_meditation.meditation_graph(data)
    return render_template("meditation.html",data=data, script=script, plot_daily_div=plot_daily_div, plot_cumu_div=plot_cumu_div, title="MEDITATION")

@app.route("/books")
def books():
    title = "BOOKS"
    return render_template("books.html",title=title)

@app.route("/goals")
def goals():
    title = "GOAL TRACKING"
    return render_template("goals.html",title=title)

@app.route("/finances")
def finances():
    title = "finances"
    return render_template("finances.html",title=title)

@app.route("/dayviewer")
def dayviewer():
    title = "Dayviewer"
    return render_template("dayviewer.html",title=title)

@app.route("/analysis_vbe")
def analysis_vbe():
    title = "Regression Models: VBE"
    return render_template("analysis_vbe.html",title=title)

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
