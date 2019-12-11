import pandas as pd
import datetime

from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, Slider, PanTool, WheelZoomTool, ResetTool, SaveTool, CustomJS
from bokeh.models.glyphs import Line
from bokeh.plotting import figure
from bokeh.charts import Line
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Div

from helper_functions import *
from config import *

def body_graph(data):
    '''Creates Bokeh plots for diet related information'''

    script_div, (div_days, div_avg_bg, div_avg_rhr, div_avg_slp_dur, div_avg_slp_q, div_days_bc, div_avg_wt, div_avg_bf, plot_blood_div, plot_rhr_div, plot_osq_div, plot_body_comp_div, plot_sleep_div, ma_slider_div) = body_figs(data)
    return script_div, div_days, div_avg_bg, div_avg_rhr, div_avg_slp_dur, div_avg_slp_q, div_days_bc, div_avg_wt, div_avg_bf, plot_blood_div, plot_rhr_div, plot_osq_div, plot_body_comp_div, plot_sleep_div, ma_slider_div

def body_figs(data, height=500, width=1200):

    #Data setup
    data['date_str'] = data['date'].map(str)
    ma_cds_working = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], bpm=data['bpm'], hrv=data['hrv'], scaled_hrv=data['scaled_hrv'], sleep_overall_q=data['sleep_overall_q'], sleep_onset=data['sleep_onset'], sleep_duration=data['sleep_duration'], sleep_how_much_more=data['sleep_how_much_more'], sleep_how_deep=data['sleep_how_deep'], sleep_interruptions=data['sleep_interruptions'], glucose=data['glucose'], ketones=data['ketones'], weight=data['weight'], bodyfat=data['bodyfat']))
    ma_cds_static = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], bpm=data['bpm'], hrv=data['hrv'], scaled_hrv=data['scaled_hrv'], sleep_overall_q=data['sleep_overall_q'], sleep_onset=data['sleep_onset'], sleep_duration=data['sleep_duration'], sleep_how_much_more=data['sleep_how_much_more'], sleep_how_deep=data['sleep_how_deep'], sleep_interruptions=data['sleep_interruptions'], glucose=data['glucose'], ketones=data['ketones'], weight=data['weight'], bodyfat=data['bodyfat']))

    #Plot tools configuration
    wz = WheelZoomTool(dimensions='width')
    plt_biomarkers_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("RHR", "@bpm{0,0} bpm"), ("Sleep Q", "@sleep_overall_q"), ("Glucose", "@glucose{0,0} mg/dl"), ("Ketones", "@ketones{1.11} mmol/L")],names=["bpm", "glucose"],mode='vline'), PanTool(dimensions='width'), wz, ResetTool(), SaveTool()]

    wz2 = WheelZoomTool(dimensions='width')
    plt_bcomp_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Weight", "@weight{1.1} lbs"), ("BF", "@bodyfat{1.1}%")],mode='vline'), PanTool(dimensions='width'), wz2, ResetTool(), SaveTool()]

    wz3 = WheelZoomTool(dimensions='width')
    plt_sleep_tools = [HoverTool(tooltips=[("Date", "@date_str"),("Sleep Quality", "@sleep_overall_q"),("Duration", "@sleep_duration"),("Satisfaction", "@sleep_how_much_more"),("Depth", "@sleep_how_deep"),("Interruptions", "@sleep_interruptions")],names=["sleep_overall_q"],mode='vline'), PanTool(dimensions='width'), wz3, ResetTool(), SaveTool()]

    #Plot Blood (glucose and ketones)
    plot_blood = figure(x_axis_type="datetime", title="Biomarkers (Various)", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, y_range=[40, 140], plot_width=int(width/2 - 50), toolbar_location="above", outline_line_color="#666666", tools=plt_biomarkers_tools, active_scroll=wz)

    plot_blood.extra_y_ranges = {"ketones_range": Range1d(start=0, end=7)}
    plot_blood.add_layout(LinearAxis(y_range_name="ketones_range"), 'right')

    plot_blood.line('date', 'glucose', name="glucose", source=ma_cds_working, line_color="#FF7700", line_width=3, line_alpha=0.6, legend="Blood Glucose")
    plot_blood.cross('date', 'ketones', source=ma_cds_working, line_color="#C74D56", line_alpha=0.6, legend="Blood Ketones", y_range_name="ketones_range")
    plot_blood.ray(x=data['date'][1195],y=.5, length=0, angle=0, line_color="#C74D56", line_width=1, y_range_name="ketones_range")
    plot_blood.ray(x=data['date'][1195],y=1, length=0, angle=0, line_color="#C74D56", line_width=1, y_range_name="ketones_range")
    plot_blood.legend.location = "top_left"
    plot_blood.legend.click_policy="hide"

    #Plot Heartrate
    plot_rhr = figure(x_axis_type="datetime", title="Morning Resting HR", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=int(height/2), plot_width=int(width/2),  x_range=plot_blood.x_range, outline_line_color="#666666")
    plot_rhr.line('date', 'bpm', name="bpm", source=ma_cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="BPM")
    plot_rhr.line('date', 'hrv', name="hrv", source=ma_cds_working, line_color="#0a8b45", line_width=3, line_alpha=0.6, legend="HRV")
    plot_rhr.line('date', 'scaled_hrv', name="scaled_hrv", source=ma_cds_working, line_color="#333366", line_width=3, line_alpha=0.6, y_range_name="scaled_hrv_range", legend="HRV (Scaled)")
    #***TODO*** Add SNS/PNS indicator
    plot_rhr.extra_y_ranges = {"scaled_hrv_range": Range1d(start=1, end=10)}
    plot_rhr.add_layout(LinearAxis(y_range_name="scaled_hrv_range"), 'right')

    plot_rhr.legend.location = "bottom_left"
    plot_rhr.legend.click_policy="hide"
    plot_rhr.toolbar_location = None

    #Plot sleep quality (single indicator)
    plot_osq = figure(x_axis_type="datetime", title="Overall Sleep Quality", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=int(height/2), plot_width=int(width/2),  y_range=[1, 9], x_range=plot_blood.x_range, outline_line_color="#666666")
    plot_osq.line('date', 'sleep_overall_q', source=ma_cds_working, line_color="#333366", line_width=3, line_alpha=0.6)
    plot_osq.toolbar_location = None

    #Plot body compostion (weight and bodyfat)
    plot_composition = figure(x_axis_type="datetime", title="Body Composition", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, y_range=[120,180], toolbar_location="above", outline_line_color="#666666", tools=plt_bcomp_tools, active_scroll=wz2)

    plot_composition.extra_y_ranges = {"bodyfat_range": Range1d(start=5, end=15)}
    plot_composition.add_layout(LinearAxis(y_range_name="bodyfat_range"), 'right')

    plot_composition.line('date', 'weight', name="weight", source=ma_cds_working, line_color="#FF7700", line_width=3, line_alpha=0.6, legend="Weight")
    plot_composition.line('date', 'bodyfat', source=ma_cds_working, line_color="#333366", line_width=3, line_alpha=0.6, legend="Bodyfat", y_range_name="bodyfat_range")
    plot_composition.legend.location = "top_left"
    plot_composition.legend.click_policy="hide"

    #Plot sleep (all indicators)
    plot_sleep = figure(x_axis_type="datetime", title="Sleep", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, y_range=[1,9], x_range=plot_blood.x_range, toolbar_location="above", outline_line_color="#666666", tools=plt_sleep_tools, active_scroll=wz3)

    plot_sleep.extra_y_ranges = {"sleep_range": Range1d(start=0, end=12)}
    plot_sleep.add_layout(LinearAxis(y_range_name="sleep_range"), 'right')

    plot_sleep.line('date', 'sleep_overall_q', name='sleep_overall_q', source=ma_cds_working, line_color="#8B0A50", line_width=2, line_alpha=0.6, legend="Sleep Quality")
    plot_sleep.line('date', 'sleep_how_much_more', source=ma_cds_working, line_color="#FF7700", line_width=2, line_alpha=0.6, legend="Satisfaction")
    plot_sleep.line('date', 'sleep_how_deep', source=ma_cds_working, line_color="#C74D56", line_width=2, line_alpha=0.6, legend="Depth")
    plot_sleep.line('date', 'sleep_interruptions', source=ma_cds_working, line_color="#0a8b45", line_width=2, line_alpha=0.6, legend="Interruptions")
    plot_sleep.line('date', 'sleep_duration', source=ma_cds_working, line_color="#333366", line_width=5, line_alpha=0.6, legend="Duration (hrs)", y_range_name="sleep_range")

    plot_sleep.legend.location = "top_left"
    plot_sleep.legend.click_policy="hide"

    #Statistics divs for the control panel
    div_days = Div()

    div_avg_bg = Div()
    div_avg_rhr = Div()

    div_avg_slp_dur = Div()
    div_avg_slp_q = Div()

    div_days_bc = Div()
    div_avg_wt = Div()
    div_avg_bf = Div()

    #Callbacks
    ma_cb = CustomJS(args=dict(w=ma_cds_working, s=ma_cds_static), code=MA_SLIDER_CODE)

    plot_blood.x_range.callback = CustomJS(args=dict(d_d=div_days, d_a_bg=div_avg_bg, d_a_r=div_avg_rhr, d_a_s_d=div_avg_slp_dur, d_a_s_q=div_avg_slp_q, s=ma_cds_static), code=BODY_STATS_CODE)
    plot_composition.x_range.callback = CustomJS(args=dict(d_d_bc=div_days_bc, d_a_wt=div_avg_wt, d_a_bf=div_avg_bf, s=ma_cds_static), code=BODY_COMP_STATS_CODE)

    ma_slider = Slider(start=1, end=30, value=7, step=1, title="Moving Average", callback=ma_cb)
    return components((div_days, div_avg_bg, div_avg_rhr, div_avg_slp_dur, div_avg_slp_q, div_days_bc, div_avg_wt, div_avg_bf, plot_blood, plot_rhr, plot_osq, plot_composition, plot_sleep, ma_slider))
