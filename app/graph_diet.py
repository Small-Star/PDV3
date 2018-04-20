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

def diet_graph(data):
    '''Creates Bokeh plots for diet related information'''

    script_div, (div_days, div_avg_intake, div_tdee, div_avg_net, div_avg_protein, div_avg_fat, div_avg_carb_all, div_avg_carb_net, div_avg_carb_fiber, div_problem_days, div_volatility, plot_comparison_div, plot_composition_div, ma_slider_div) = diet_figs(data)

    return script_div, div_days, div_avg_intake, div_tdee, div_avg_net, div_avg_protein, div_avg_fat, div_avg_carb_all, div_avg_carb_net, div_avg_carb_fiber, div_problem_days, div_volatility, plot_comparison_div, plot_composition_div, ma_slider_div

def diet_figs(data, height=500, width=1200):

    data['date_str'] = data['date'].map(str)


    wz = WheelZoomTool(dimensions='width')
    plt_comparison_tools = [HoverTool(tooltips=[("Date", "@date_str"), ("Intake", "@kcal_intake{1} kcal"), ("TDEE", "@tdee{1} kcal")],names=["kcal_intake"],mode='vline'),
    PanTool(dimensions='width'),
    wz,
    ResetTool(),
    SaveTool()]

    wz2 = WheelZoomTool(dimensions='width')
    plt_composition_tools = [HoverTool(tooltips=[("Date", "@date_str"),("Intake", "@kcal_intake kcal"),("Protein", "@protein_g{0,0}g"),("Net Carbs", "@net_carb_g{0,0}g"),("Fat", "@fat_g{0,0}g")],names=["kcal_intake"],mode='vline'),
    PanTool(dimensions='width'),
    wz2,
    ResetTool(),
    SaveTool()]



    ma_cds_working = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], kcal_intake=data['kcal_intake'], tdee=data['tdee'], protein_g=data['protein_intake'], protein_intake=data['protein_intake'].transform(lambda x: x*ACF_P), net_carb_g=data['net_carb_intake'], net_carb_intake=data['net_carb_intake'].transform(lambda x: x*ACF_C), carb_g=data['carb_intake'], fat_g=data['fat_intake'], fat_intake=data['fat_intake'].transform(lambda x: x*ACF_F), net_intake=data['net_intake'], fiber_g=data['fiber_intake']))
    ma_cds_static = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], kcal_intake=data['kcal_intake'], tdee=data['tdee'], protein_g=data['protein_intake'], protein_intake=data['protein_intake'].transform(lambda x: x*ACF_P), net_carb_g=data['net_carb_intake'], net_carb_intake=data['net_carb_intake'].transform(lambda x: x*ACF_C), carb_g=data['carb_intake'], fat_g=data['fat_intake'], fat_intake=data['fat_intake'].transform(lambda x: x*ACF_F), net_intake=data['net_intake'], fiber_g=data['fiber_intake']))

    y_fudge = 1.1
    y_r_upper = max(ma_cds_working.data['kcal_intake'].max()*y_fudge,ma_cds_working.data['tdee'].max()*y_fudge)
    y_r_lower = ma_cds_working.data['net_intake'].min()*y_fudge

    plot_comparison = figure(x_axis_type="datetime", title="Intake/Output Comparison (kcal)", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, y_range=[y_r_lower, y_r_upper], toolbar_location="above", outline_line_color="#666666", tools=plt_comparison_tools, active_scroll=wz)

    plot_comparison.line('date', 'kcal_intake', name="kcal_intake", source=ma_cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="Total Intake")
    plot_comparison.line('date', 'tdee', source=ma_cds_working, line_color="#333366", line_width=3, line_alpha=0.6, legend="TDEE")
    plot_comparison.line('date', 'net_intake', source=ma_cds_working, line_color="#FF7700", line_width=3, line_alpha=0.6, legend="Net Intake")
    plot_comparison.legend.location = "top_left"
    plot_comparison.legend.click_policy="hide"

    plot_composition = figure(x_axis_type="datetime", title="Intake Composition (kcal)", h_symmetry=False, v_symmetry=False,
                  min_border=0, plot_height=height, plot_width=width, y_range=[0, y_r_upper], x_range=plot_comparison.x_range, toolbar_location="above", outline_line_color="#666666", tools=plt_composition_tools, active_scroll=wz2)

    plot_composition.line('date', 'kcal_intake', name="kcal_intake", source=ma_cds_working, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="Total Intake")
    plot_composition.line('date', 'protein_intake', source=ma_cds_working, line_color="#333366", line_width=2, line_alpha=0.6, legend="Protein")
    plot_composition.line('date', 'net_carb_intake', source=ma_cds_working, line_color="#FF7700", line_width=2, line_alpha=0.6, legend="Net Carb Intake")
    plot_composition.line('date', 'fat_intake', source=ma_cds_working, line_color="#C74D56", line_width=2, line_alpha=0.6, legend="Fat Intake")

    plot_composition.legend.location = "top_left"
    plot_composition.legend.click_policy="hide"

    div_days = Div()
    div_avg_intake = Div()
    div_tdee = Div()
    div_avg_net = Div()
    div_avg_protein = Div()
    div_avg_fat = Div()
    div_avg_carb_all = Div()
    div_avg_carb_net = Div()
    div_avg_carb_fiber = Div()
    div_problem_days = Div()
    div_volatility = Div()

    ma_cb = CustomJS(args=dict(w=ma_cds_working, s=ma_cds_static), code=MA_SLIDER_CODE)

    plot_comparison.x_range.callback = CustomJS(args=dict(d_d=div_days, d_a_i=div_avg_intake, d_t=div_tdee, d_a_n=div_avg_net, d_a_p=div_avg_protein, d_a_f=div_avg_fat, d_a_c_a=div_avg_carb_all, d_a_c_n=div_avg_carb_net, d_a_c_f=div_avg_carb_fiber, d_p_d=div_problem_days, d_v=div_volatility, s=ma_cds_static), code=DIET_STATS_CODE)
    ma_slider = Slider(start=1, end=30, value=7, step=1, title="Moving Average", callback=ma_cb)
    return components((div_days, div_avg_intake, div_tdee, div_avg_net, div_avg_protein, div_avg_fat, div_avg_carb_all, div_avg_carb_net, div_avg_carb_fiber, div_problem_days, div_volatility, plot_comparison, plot_composition, ma_slider))
