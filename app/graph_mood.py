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

def mood_graph(data):
    '''Creates a Bokeh plot for mood data'''


    #TODO: This is messy; clean up
    # cleaned_data = {"date": [], "date_str": [],
    #     "a_l_working": [], "a_u_working": [], "a_be_working": [], "v_l_working": [], "v_u_working": [], "v_be_working": [],
    #     "a_l_static": [], "a_u_static": [], "a_be_static": [], "v_l_static": [], "v_u_static": [], "v_be_static": []}
    # for i in range(len(data)):
    #     cleaned_data['date'].append(data[i].date)
    #     cleaned_data['date_str'].append(str(data[i].date))
    #     cleaned_data['a_l_working'].append(data[i].a_l)
    #     cleaned_data['a_u_working'].append(data[i].a_u)
    #     cleaned_data['a_be_working'].append(data[i].a_be)
    #     cleaned_data['v_l_working'].append(data[i].v_l)
    #     cleaned_data['v_u_working'].append(data[i].v_u)
    #     cleaned_data['v_be_working'].append(data[i].v_be)
    #
    #     #Add in an extra copy of data to have an unmodified copy to work from
    #     cleaned_data['a_l_static'].append(data[i].a_l)
    #     cleaned_data['a_u_static'].append(data[i].a_u)
    #     cleaned_data['a_be_static'].append(data[i].a_be)
    #     cleaned_data['v_l_static'].append(data[i].v_l)
    #     cleaned_data['v_u_static'].append(data[i].v_u)
    #     cleaned_data['v_be_static'].append(data[i].v_be)
    #
    # df = pd.DataFrame(cleaned_data, columns = ['date','date_str', 'a_l_working', 'a_u_working', 'a_be_working', 'v_l_working', 'v_u_working', 'v_be_working', 'a_l_static', 'a_u_static', 'a_be_static', 'v_l_static', 'v_u_static', 'v_be_static'])



    script_div, (div_days, div_avg_a, div_avg_v, div_good_days, div_poor_days, div_caution_days, div_warning_days, plot_ts_div, plot_vr_div, ma_slider_div) = mood_figs(data)

    return script_div, div_days, div_avg_a, div_avg_v, div_good_days, div_poor_days, div_caution_days, div_warning_days, plot_ts_div, plot_vr_div, ma_slider_div


def mood_figs(data, height = 500, width = 1200):



    #Timeseries Plot
    wz = WheelZoomTool(dimensions='width')
    plot_ts_tools = [HoverTool(tooltips=[("Date", "@date_str"),("A", "@a_l:@a_u (@a_be)"),("V", "@v_l:@v_u (@v_be)")]),
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

    #***TODO IMPROVE: Hookup slider
    alpha_fudge, color_fudge = .1, 150
    cds_working_2 = ColumnDataSource(cds_working.data)
    d = cds_working_2.data

    def get_oval(a_l, a_u, v_l, v_u, v_be, a_be):
        x = float((a_u + a_l)/2)
        y = float((v_u + v_l)/2)
        w = (a_u - a_l)
        h = (v_u - v_l)
        alpha = float((1 + abs(5 - a_be)**4)*alpha_fudge) #***TODO FIX: Indicate better

        c_val = float((1 + abs(5 - v_be)**4)*color_fudge)

        #Some bug in Bokeh or something; does not accept (R,G,B) tuples as colors
        if v_be >= 5:
            color = "#%02x%02x%02x" % (0,c_val,0)
        else:
            color = "#%02x%02x%02x" % (c_val,0,0)

        return x, y, w, h, alpha, color

    x, y, w, h, alpha, color = [], [], [], [], [], []
    for c in range(len(d['date'])):
        x_, y_, w_, h_, alpha_, color_ = get_oval(d['a_l'][c], d['a_u'][c], d['v_l'][c], d['v_u'][c], d['v_be'][c], d['a_be'][c])
        x.append(x_)
        y.append(y_)
        w.append(w_)
        h.append(h_)
        alpha.append(alpha_)
        color.append(color_)

    cds_working_2.add(x,name='x')
    cds_working_2.add(y,name='y')
    cds_working_2.add(w,name='w')
    cds_working_2.add(h,name='h')
    cds_working_2.add(alpha,name='alpha')
    cds_working_2.add(color,name='color')

    plot_vr.oval('x','y','w','h',color='color', source=cds_working_2, alpha='alpha')

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
