import pandas as pd
import datetime

from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, Slider, PanTool, WheelZoomTool, ResetTool, SaveTool, CustomJS
from bokeh.models.glyphs import Line
from bokeh.plotting import figure
from bokeh.charts import Line
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource

from helper_functions import *
from config import *

def diet_graph(data):
    '''Creates Bokeh plots for diet related information'''

    stats = diet_stats(data)

    script_div, (plot_comparison_div, plot_composition_div, ma_slider_div) = diet_figs(data)

    return stats, script_div, plot_comparison_div, plot_composition_div, ma_slider_div

def diet_figs(data, height=500, width=1200):
    wz = WheelZoomTool(dimensions='width')
    plt_comparison_tools = [HoverTool(tooltips=[("Date", "@date"), ("Intake (kcal)", "@kcal_intake"), ("TDEE (kcal)", "@tdee")]),
    PanTool(dimensions='width'),
    wz,
    ResetTool(),
    SaveTool()]

    wz2 = WheelZoomTool(dimensions='width')
    plt_composition_tools = [HoverTool(tooltips=[("Date", "@date"),("Intake (kcal)", "@kcal_intake"),("Protein", "@protein_intake"),("Net Carbs", "@net_carb_intake"),("Fat", "@fat_intake")]),
    PanTool(dimensions='width'),
    wz2,
    ResetTool(),
    SaveTool()]

    ma_cds_working = ColumnDataSource(dict(date=data['date'], kcal_intake=data['kcal_intake'], tdee=data['tdee'], protein_intake=data['protein_intake'].transform(lambda x: x*ACF_P), net_carb_intake=data['net_carb_intake'].transform(lambda x: x*ACF_C), fat_intake=data['fat_intake'].transform(lambda x: x*ACF_F), net_intake=data['net_intake']))
    ma_cds_static = ColumnDataSource(dict(date=data['date'], kcal_intake=data['kcal_intake'], tdee=data['tdee'], protein_intake=data['protein_intake'].transform(lambda x: x*ACF_P), net_carb_intake=data['net_carb_intake'].transform(lambda x: x*ACF_C), fat_intake=data['fat_intake'].transform(lambda x: x*ACF_F), net_intake=data['net_intake']))

    y_fudge = 1.1
    y_r_upper = max(data['kcal_intake'].max()*y_fudge,data['tdee'].max()*y_fudge)
    y_r_lower = data['net_intake'].min()*y_fudge

    plot_comparison = figure(x_axis_type="datetime", title="Intake/Output Comparison", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, y_range=[y_r_lower, y_r_upper], toolbar_location="above", outline_line_color="#666666", tools=plt_comparison_tools, active_scroll=wz)

    plot_comparison.line('date', 'kcal_intake', source=ma_cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="Total Intake (kcal)")
    plot_comparison.line('date', 'tdee', source=ma_cds_working, line_color="#333366", line_width=3, line_alpha=0.6, legend="TDEE (kcal)")
    plot_comparison.line('date', 'net_intake', source=ma_cds_working, line_color="#FF7700", line_width=3, line_alpha=0.6, legend="Net Intake (kcal)")
    plot_comparison.legend.location = "top_left"

    plot_composition = figure(x_axis_type="datetime", title="Intake Composition", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, y_range=[0, y_r_upper], toolbar_location="above", outline_line_color="#666666", tools=plt_composition_tools, active_scroll=wz2)

    plot_composition.line('date', 'kcal_intake', source=ma_cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="Total Intake (kcal)")
    plot_composition.line('date', 'protein_intake', source=ma_cds_working, line_color="#333366", line_width=2, line_alpha=0.6, legend="Protein (g)")
    plot_composition.line('date', 'net_carb_intake', source=ma_cds_working, line_color="#FF7700", line_width=2, line_alpha=0.6, legend="Net Carb Intake (g)")
    plot_composition.line('date', 'fat_intake', source=ma_cds_working, line_color="#C74D56", line_width=2, line_alpha=0.6, legend="Fat Intake (g)")

    plot_composition.legend.location = "top_left"
    plot_composition.legend.click_policy="hide"

    ma_cb = CustomJS(args=dict(w=ma_cds_working, s=ma_cds_static), code=MA_SLIDER_CODE)

    ma_slider = Slider(start=1, end=30, value=7, step=1, title="Moving Average", callback=ma_cb)
    return components((plot_comparison, plot_composition, ma_slider))

def diet_stats(data):
    stats = {}
    stats['days'] = len(data['date'])
    stats['avg_intake'] = round(data['kcal_intake'].mean(),2)
    stats['avg_tdee'] = round(data['tdee'].mean())
    stats['avg_net'] = round(data['net_intake'].mean())
    stats['avg_protein'] = round(data['protein_intake'].mean())
    stats['avg_fat'] = round(data['fat_intake'].mean())
    stats['avg_carb'] = round(data['carb_intake'].mean())
    stats['avg_net_carb'] = round(data['net_carb_intake'].mean())
    stats['avg_fiber'] = round(data['fiber_intake'].mean())
    stats['problem_days'] = sum(data['kcal_intake'].gt(4000))
    return stats
