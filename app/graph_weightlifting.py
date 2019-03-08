import pandas as pd
import datetime

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
    plot_max_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Squat", "@squat_max")]), PanTool(dimensions='width'), wz_max, ResetTool(), SaveTool()]

    wz_mvps = WheelZoomTool(dimensions='width')
    plot_mvps_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Squat", "@squat_max_vol_per_set")]), PanTool(dimensions='width'), wz_mvps, ResetTool(), SaveTool()]

    wz_tv = WheelZoomTool(dimensions='width')
    plot_tv_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Squat", "@squat_total_vol")]), PanTool(dimensions='width'), wz_tv, ResetTool(), SaveTool()]

    data['date_str'] = data['date'].map(str)

    cds_max = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], squat_max=data['squat_max']))

    plot_max = figure(x_axis_type="datetime", title="MAXes", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", tools=plot_max_tools, active_scroll=wz_max)
    plot_max.line('date', 'squat_max', source=cds_max, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat Max (lbs)")

    glyph = X(x='date', y='squat_max', line_color="#8B0A50", line_width=1, line_alpha=0.6)
    plot_max.add_glyph(cds_max, glyph)
    plot_max.legend.location = "top_left"
    plot_max.legend.click_policy="hide"

    cds_mvps = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], squat_max_vol_per_set=data['squat_max_vol_per_set']))

    plot_mvps = figure(x_axis_type="datetime", title="Maximum Volume Per Set", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", tools=plot_mvps_tools, active_scroll=wz_mvps)

    plot_mvps.line('date', 'squat_max_vol_per_set', source=cds_mvps, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat MVPS (lbs)")
    glyph = X(x='date', y='squat_max_vol_per_set', line_color="#8B0A50", line_width=1, line_alpha=0.6)
    plot_mvps.add_glyph(cds_mvps, glyph)

    plot_mvps.legend.location = "top_left"
    plot_mvps.legend.click_policy="hide"

    cds_tv = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], squat_total_vol=data['squat_total_vol']))

    plot_tv = figure(x_axis_type="datetime", title="Total Volume", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", tools=plot_tv_tools, active_scroll=wz_tv)

    plot_tv.line('date', 'squat_total_vol', source=cds_tv, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Total Squat Volume (lbs)")
    glyph = X(x='date', y='squat_total_vol', line_color="#8B0A50", line_width=1, line_alpha=0.6)
    plot_tv.add_glyph(cds_tv, glyph)

    plot_tv.legend.location = "top_left"
    plot_tv.legend.click_policy="hide"

    div_max = Div()
    div_max_vol_per_set = Div()
    div_total_vol = Div()

    return components((div_max, div_max_vol_per_set, div_total_vol, plot_max, plot_mvps, plot_tv))
