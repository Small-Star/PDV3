import pandas as pd
import datetime
import math

from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, Slider, PanTool, WheelZoomTool, ResetTool, SaveTool, CustomJS
from bokeh.models.glyphs import Line
from bokeh.models.markers import X
from bokeh.plotting import figure
from bokeh.charts import Line
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Div

from helper_functions import *

def weightlifting_graph(data):
	'''Weightlifting graphs'''
	script_div, (div_max, div_max_vol_per_set, div_total_volume, plot_max_div, plot_mvps_div, plot_tv_div) = weightlifting_figs(data)
	return script_div, div_max, div_max_vol_per_set, div_total_volume, plot_max_div, plot_mvps_div, plot_tv_div


def weightlifting_figs(data, height = 500, width = 1200):
    #Timeseries Plot
    wz_max = WheelZoomTool(dimensions='width')

    wz_mvps = WheelZoomTool(dimensions='width')
    plot_mvps_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Squat", "@squat_max_vol_per_set"), ("Deadlift", "@deadlift_max_vol_per_set"), ("Bench Press", "@bench_max_vol_per_set"), ("OHP", "@ohp_max_vol_per_set")]), PanTool(dimensions='width'), wz_mvps, ResetTool(), SaveTool()]

    wz_tv = WheelZoomTool(dimensions='width')
    plot_tv_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Squat", "@squat_total_vol"), ("Deadlift", "@deadlift_total_vol"), ("Bench Press", "@bench_total_vol"), ("OHP", "@ohp_total_vol")]), PanTool(dimensions='width'), wz_tv, ResetTool(), SaveTool()]

    data['date_str'] = data['date'].map(str)

    cds_max = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], squat_max=data['squat_max'], deadlift_max=data['deadlift_max'], bench_max=data['bench_max'], ohp_max=data['ohp_max']))

    d = cds_max.data

    s_m, d_m, b_m, o_m = [], [], [], []
    s_m.append(155.0)
    d_m.append(145.0)
    b_m.append(135.0)
    o_m.append(70.0)

    for c in range(1,len(d['date'])):
    	if math.isnan(d['squat_max'][c]):
    		s_m.append(max(s_m[c - 1], s_m[0]))
    	else:
    		s_m.append(max(s_m[c - 1],d['squat_max'][c]))
    	if math.isnan(d['deadlift_max'][c]):
    		d_m.append(max(d_m[c - 1], d_m[0]))
    	else:
    		d_m.append(max(d_m[c - 1],d['deadlift_max'][c])) 
    	if math.isnan(d['bench_max'][c]):
    		b_m.append(max(b_m[c - 1], b_m[0]))
    	else:
    		b_m.append(max(b_m[c - 1],d['bench_max'][c]))
    	if math.isnan(d['ohp_max'][c]):
    		o_m.append(max(o_m[c - 1], o_m[0]))
    	else:
    		o_m.append(max(o_m[c - 1],d['ohp_max'][c]))

    #cds_max_working = ColumnDataSource()
    cds_max.add(d['date'], name='date')
    cds_max.add(s_m, name='s_m')
    cds_max.add(d_m, name='d_m')
    cds_max.add(b_m, name='b_m')
    cds_max.add(o_m, name='o_m')

    plot_max = figure(x_axis_type="datetime", title="MAXes", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", active_scroll=wz_max)
    
    plot_max.yaxis.axis_label = "lbs"

    cr = plot_max.circle('date', 'squat_max', source=cds_max, size=20, fill_color="grey", hover_fill_color="firebrick", fill_alpha=0.05, hover_alpha=0.3, line_color=None, hover_line_color="white")
    plot_max_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Squat", "@squat_max"), ("Deadlift", "@deadlift_max"), ("Bench Press", "@bench_max"), ("OHP", "@ohp_max")], renderers=[cr], mode='vline'), PanTool(dimensions='width'), wz_max, ResetTool(), SaveTool()]
    plot_max.add_tools(plot_max_tools[0])
    plot_max.line('date', 's_m', source=cds_max, line_color="#8B0A50", line_width=2, line_alpha=0.6, legend="Squat (Clamp)")
    plot_max.cross('date', 'squat_max', source=cds_max, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat (Actual)")    

    plot_max.line('date', 'd_m', source=cds_max, line_color="#333366", line_width=2, line_alpha=0.6, legend="Deadlift (Clamp)")
    plot_max.cross('date', 'deadlift_max', source=cds_max, line_color="#333366", line_width=1, line_alpha=0.6, legend="Deadlift (Actual)")    

    plot_max.line('date', 'b_m', source=cds_max, line_color="#FF7700", line_width=2, line_alpha=0.6, legend="Bench Press (Clamp)")
    plot_max.cross('date', 'bench_max', source=cds_max, line_color="#FF7700", line_width=1, line_alpha=0.6, legend="Bench Press (Actual)")    

    plot_max.line('date', 'o_m', source=cds_max, line_color="#C74D56", line_width=2, line_alpha=0.6, legend="OHP (Clamp)")
    plot_max.cross('date', 'ohp_max', source=cds_max, line_color="#C74D56", line_width=1, line_alpha=0.6, legend="OHP (Actual)")    

    plot_max.legend.location = "top_left"
    plot_max.legend.click_policy="hide"

    cds_mvps = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], squat_max_vol_per_set=data['squat_max_vol_per_set']))

    plot_mvps = figure(x_axis_type="datetime", title="Maximum Volume Per Set", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", tools=plot_mvps_tools, active_scroll=wz_mvps)

    plot_mvps.line('date', 'squat_max_vol_per_set', source=cds_mvps, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat (lbs)")
    glyph = X(x='date', y='squat_max_vol_per_set', line_color="#8B0A50", line_width=1, line_alpha=0.6)
    plot_mvps.add_glyph(cds_mvps, glyph)

    plot_mvps.legend.location = "top_left"
    plot_mvps.legend.click_policy="hide"

    cds_tv = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], squat_total_vol=data['squat_total_vol']))

    plot_tv = figure(x_axis_type="datetime", title="Total Volume", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", tools=plot_tv_tools, active_scroll=wz_tv)

    plot_tv.line('date', 'squat_total_vol', source=cds_tv, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat (lbs)")
    glyph = X(x='date', y='squat_total_vol', line_color="#8B0A50", line_width=1, line_alpha=0.6)
    plot_tv.add_glyph(cds_tv, glyph)

    plot_tv.legend.location = "top_left"
    plot_tv.legend.click_policy="hide"

    div_max = Div()
    div_max_vol_per_set = Div()
    div_total_vol = Div()


    return components((div_max, div_max_vol_per_set, div_total_vol, plot_max, plot_mvps, plot_tv))
