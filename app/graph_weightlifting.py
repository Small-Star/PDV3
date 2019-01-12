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

def weightlifting_graph(data):
	script_div, (plot_graph_div, plot_battleship_div, div_max, div_max_vol_per_set, div_total_volume) = weightlifting_figs(data)
    return script_div, plot_graph_div, plot_battleship_div, div_max, div_max_vol_per_set, div_total_volume


def weightlifting_figs(data, height = 500, width = 1200):
    #Timeseries Plot
    wz = WheelZoomTool(dimensions='width')
    plot_ts_tools = [HoverTool(tooltips=[("Date", "@date_str")]),
    PanTool(dimensions='width'),
    wz,
    ResetTool(),
    SaveTool()]

    data['date_str'] = data['date'].map(str)

    cds_working = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], a_l=data['a_l'], a_u=data['a_u'], a_be=data['a_be'], v_l=data['v_l'], v_u=data['v_u'], v_be=data['v_be']))
    cds_static = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], a_l=data['a_l'], a_u=data['a_u'], a_be=data['a_be'], v_l=data['v_l'], v_u=data['v_u'], v_be=data['v_be']))

    plot_ts = figure(x_axis_type="datetime", title="Mood (AV Circumplex Model)", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, y_range=[1,9], toolbar_location="above", outline_line_color="#666666", tools=plot_ts_tools, active_scroll=wz)

    plot_ts.line('date', 'a_l', source=cds_working, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="A (Lower Bound)")
    plot_ts.line('date', 'a_u', source=cds_working, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="A (Upper Bound)")
    plot_ts.line('date', 'a_be', source=cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="A (Best Est.)")

    plot_ts.line('date', 'v_l', source=cds_working, line_color="#00E5EE", line_width=1, line_alpha=0.6, legend="V (Lower Bound)")
    plot_ts.line('date', 'v_u', source=cds_working, line_color="#00E5EE", line_width=1, line_alpha=0.6, legend="V (Upper Bound)")
    plot_ts.line('date', 'v_be', source=cds_working, line_color="#00E5EE", line_width=3, line_alpha=0.6, legend="V (Best Est.)")

    plot_ts.legend.location = "top_left"
    plot_ts.legend.click_policy="hide"

    #Vis_Rep Plot
    plot_vr = figure(title="Mood (AV Circumplex Model)", h_symmetry=False, v_symmetry=False,
                      min_border=0, plot_height=height, plot_width=width, x_range=[1,9], y_range=[1,9], toolbar_location="above", outline_line_color="#666666", x_axis_label='Alertness', y_axis_label="Valence")

    div_days = Div()
    div_avg_a = Div()
    div_avg_v = Div()
    div_good_days = Div()
    div_poor_days = Div()
    div_caution_days = Div()
    div_warning_days = Div()

    ma_cb = CustomJS(args=dict(w=cds_working, s=cds_static), code=MA_SLIDER_CODE)
    plot_ts.x_range.callback = CustomJS(args=dict(d_d=div_days, d_avg_a=div_avg_a, d_avg_v=div_avg_v, d_g_d=div_good_days, d_p_d=div_poor_days, d_c_d=div_caution_days, d_w_d=div_warning_days, s=cds_static), code=MOOD_STATS_CODE)
    ma_slider = Slider(start=1, end=30, value=1, step=1, title="Moving Average", callback=ma_cb)
    return components((div_days, div_avg_a, div_avg_v, div_good_days, div_poor_days, div_caution_days, div_warning_days, plot_ts, plot_vr, ma_slider))
