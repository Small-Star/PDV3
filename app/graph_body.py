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

    script_div, (div, plot_blood_div, plot_rhr_div, plot_osq_div, plot_body_comp_div, plot_sleep_div, ma_slider_div) = body_figs(data)
    return script_div, div, plot_blood_div, plot_rhr_div, plot_osq_div, plot_body_comp_div, plot_sleep_div, ma_slider_div

def body_figs(data, height=500, width=1200):

    data['date_str'] = data['date'].map(str)


    wz = WheelZoomTool(dimensions='width')
    plt_biomarkers_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("RHR", "@bpm"), ("Sleep Quality", "@sleep_overall_q"), ("Blood Glucose", "@glucose"), ("Blood Ketones", "@ketones")],names=["bpm", "glucose"],mode='vline'),
    PanTool(dimensions='width'),
    wz,
    ResetTool(),
    SaveTool()]

    wz2 = WheelZoomTool(dimensions='width')
    plt_bcomp_tools = [HoverTool(tooltips=[("Date", "@date_str")],mode='vline'),
    PanTool(dimensions='width'),
    wz2,
    ResetTool(),
    SaveTool()]

    wz3 = WheelZoomTool(dimensions='width')
    plt_sleep_tools = [HoverTool(tooltips=[("Date", "@date_str"),("Sleep Quality", "@sleep_overall_q"),("Duration", "@sleep_duration"),("Satisfaction", "@sleep_how_much_more"),("Depth", "@sleep_how_deep"),("Interruptions", "@sleep_interruptions")],names=["sleep_overall_q"],mode='vline'),
    PanTool(dimensions='width'),
    wz3,
    ResetTool(),
    SaveTool()]

    ma_cds_working = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], bpm=data['bpm'], sleep_overall_q=data['sleep_overall_q'], sleep_onset=data['sleep_onset'], sleep_duration=data['sleep_duration'], sleep_how_much_more=data['sleep_how_much_more'], sleep_how_deep=data['sleep_how_deep'], sleep_interruptions=data['sleep_interruptions'], glucose=data['glucose'], ketones=data['ketones']))
    ma_cds_static = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], bpm=data['bpm'], sleep_overall_q=data['sleep_overall_q'], sleep_onset=data['sleep_onset'], sleep_duration=data['sleep_duration'], sleep_how_much_more=data['sleep_how_much_more'], sleep_how_deep=data['sleep_how_deep'], sleep_interruptions=data['sleep_interruptions'], glucose=data['glucose'], ketones=data['ketones']))

    # y_fudge = 1.1
    # y_r_upper = max(ma_cds_working.data['kcal_intake'].max()*y_fudge,ma_cds_working.data['tdee'].max()*y_fudge)
    # y_r_lower = ma_cds_working.data['net_intake'].min()*y_fudge

    plot_blood = figure(x_axis_type="datetime", title="Biomarkers (Various)", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, y_range=[40, 140], plot_width=int(width/2 - 50), toolbar_location="above", outline_line_color="#666666", tools=plt_biomarkers_tools, active_scroll=wz)


    plot_blood.extra_y_ranges = {"ketones_range": Range1d(start=0, end=7)}
    plot_blood.add_layout(LinearAxis(y_range_name="ketones_range"), 'right')

    plot_blood.line('date', 'glucose', name="glucose", source=ma_cds_working, line_color="#FF7700", line_width=3, line_alpha=0.6, legend="Blood Glucose")
    plot_blood.cross('date', 'ketones', source=ma_cds_working, line_color="#C74D56", line_alpha=0.6, legend="Blood Ketones", y_range_name="ketones_range")
    plot_blood.ray(x=data['date'][1195],y=.5, length=0, angle=0, line_color="#C74D56", line_width=1, y_range_name="ketones_range")
    plot_blood.ray(x=data['date'][1195],y=1, length=0, angle=0, line_color="#C74D56", line_width=1, y_range_name="ketones_range")
    plot_blood.legend.location = "top_left"
    plot_blood.legend.click_policy="hide"

    plot_rhr = figure(x_axis_type="datetime", title="Morning Resting HR", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=int(height/2), plot_width=int(width/2),  x_range=plot_blood.x_range, outline_line_color="#666666")
    plot_rhr.line('date', 'bpm', name="bpm", source=ma_cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6)
    plot_rhr.toolbar_location = None

    plot_osq = figure(x_axis_type="datetime", title="Overall Sleep Quality", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=int(height/2), plot_width=int(width/2),  y_range=[1, 9], x_range=plot_blood.x_range, outline_line_color="#666666")
    plot_osq.line('date', 'sleep_overall_q', source=ma_cds_working, line_color="#333366", line_width=3, line_alpha=0.6)
    plot_osq.toolbar_location = None

    plot_composition = figure(x_axis_type="datetime", title="Body Composition", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, x_range=plot_blood.x_range, toolbar_location="above", outline_line_color="#666666", tools=plt_bcomp_tools, active_scroll=wz2)

    plot_composition.legend.location = "top_left"
    plot_composition.legend.click_policy="hide"

    plot_sleep = figure(x_axis_type="datetime", title="Sleep", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, y_range=[1,9], x_range=plot_blood.x_range, toolbar_location="above", outline_line_color="#666666", tools=plt_sleep_tools, active_scroll=wz3)

    plot_sleep.extra_y_ranges = {"sleep_range": Range1d(start=0, end=12)}
    plot_sleep.add_layout(LinearAxis(y_range_name="sleep_range"), 'right')

    plot_sleep.line('date', 'sleep_overall_q', name='sleep_overall_q', source=ma_cds_working, line_color="#8B0A50", line_width=2, line_alpha=0.6, legend="Sleep Quality")
    plot_sleep.line('date', 'sleep_duration', source=ma_cds_working, line_color="#333366", line_width=2, line_alpha=0.6, legend="Duration (hrs)", y_range_name="sleep_range")
    plot_sleep.line('date', 'sleep_how_much_more', source=ma_cds_working, line_color="#FF7700", line_width=2, line_alpha=0.6, legend="Satisfaction")
    plot_sleep.line('date', 'sleep_how_deep', source=ma_cds_working, line_color="#C74D56", line_width=2, line_alpha=0.6, legend="Depth")
    plot_sleep.line('date', 'sleep_interruptions', source=ma_cds_working, line_color="#0a8b45", line_width=2, line_alpha=0.6, legend="Interruptions")

    plot_sleep.legend.location = "top_left"
    plot_sleep.legend.click_policy="hide"

    ma_cb = CustomJS(args=dict(w=ma_cds_working, s=ma_cds_static), code=MA_SLIDER_CODE)
    div = Div()
    plot_blood.x_range.callback = CustomJS(args=dict(d_d=div, s=ma_cds_static), code=BODY_STATS_CODE)
    ma_slider = Slider(start=1, end=30, value=7, step=1, title="Moving Average", callback=ma_cb)
    return components((div, plot_blood, plot_rhr, plot_osq, plot_composition, plot_sleep, ma_slider))
