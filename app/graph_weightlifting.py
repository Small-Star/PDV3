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
	script_div, (div_stairs, div_num_ohp, div_workouts, div_squat_max, div_deadlift_max, div_bench_max, div_ohp_max, div_squat_max_vol_per_set, div_deadlift_max_vol_per_set, div_bench_max_vol_per_set, div_ohp_max_vol_per_set, div_squat_total_vol, div_deadlift_total_vol, div_bench_total_vol, div_ohp_total_vol, plot_max_div, plot_mvps_div, plot_tv_div, ma_slider_div) = weightlifting_figs(data)
	return script_div, div_stairs, div_num_ohp, div_workouts, div_squat_max, div_deadlift_max, div_bench_max, div_ohp_max, div_squat_max_vol_per_set, div_deadlift_max_vol_per_set, div_bench_max_vol_per_set, div_ohp_max_vol_per_set, div_squat_total_vol, div_deadlift_total_vol, div_bench_total_vol, div_ohp_total_vol, plot_max_div, plot_mvps_div, plot_tv_div, ma_slider_div


def weightlifting_figs(data, height = 500, width = 1200):
	#Timeseries Plot
	wz_max = WheelZoomTool(dimensions='width')
	plot_max_tools_s = [HoverTool(tooltips=[("Squat", "@s_m : @squat_max")], names=["squat_clamp"],mode='vline'), PanTool(dimensions='width'), wz_max, ResetTool(), SaveTool()]
	plot_max_tools_d = [HoverTool(tooltips=[("Deadlift", "@d_m : @deadlift_max"), (" ", " ")], names=["deadlift_clamp"],mode='vline'), PanTool(dimensions='width'), wz_max, ResetTool(), SaveTool()]
	plot_max_tools_b = [HoverTool(tooltips=[("Bench Press", "@b_m : @bench_max")], names=["bench_clamp"],mode='vline'), PanTool(dimensions='width'), wz_max, ResetTool(), SaveTool()]
	plot_max_tools_o = [HoverTool(tooltips=[("OHP", "@o_m : @ohp_max")], names=["ohp_clamp"],mode='vline'), PanTool(dimensions='width'), wz_max, ResetTool(), SaveTool()]


	wz_mvps = WheelZoomTool(dimensions='width')
	plot_mvps_tools_s = [HoverTool(tooltips=[("Squat", "@s_mvps{1} : @squat_max_vol_per_set{1}")], names=["s_mvps"],mode='vline'), PanTool(dimensions='width'), wz_mvps, ResetTool(), SaveTool()]
	plot_mvps_tools_d = [HoverTool(tooltips=[("Deadlift", "@d_mvps{1} : @deadlift_max_vol_per_set{1}")], names=["d_mvps"],mode='vline'), PanTool(dimensions='width'), wz_mvps, ResetTool(), SaveTool()]
	plot_mvps_tools_b = [HoverTool(tooltips=[("Bench Press", "@b_mvps{1} : @bench_max_vol_per_set{1}")], names=["b_mvps"],mode='vline'), PanTool(dimensions='width'), wz_mvps, ResetTool(), SaveTool()]
	plot_mvps_tools_o = [HoverTool(tooltips=[("OHP", "@o_mvps{1} : @ohp_max_vol_per_set{1}")], names=["o_mvps"],mode='vline'), PanTool(dimensions='width'), wz_mvps, ResetTool(), SaveTool()]

	wz_tv = WheelZoomTool(dimensions='width')
	plot_tv_tools_s = [HoverTool(tooltips=[("Squat", "@s_tv{1} : @squat_total_vol{1}")], names=["s_tv"],mode='vline'), PanTool(dimensions='width'), wz_tv, ResetTool(), SaveTool()]
	plot_tv_tools_d = [HoverTool(tooltips=[("Deadlift", "@d_tv{1} : @deadlift_total_vol{1}")], names=["d_tv"],mode='vline'), PanTool(dimensions='width'), wz_tv, ResetTool(), SaveTool()]
	plot_tv_tools_b = [HoverTool(tooltips=[("Bench Press", "@b_tv{1} : @bench_total_vol{1}")], names=["b_tv"],mode='vline'), PanTool(dimensions='width'), wz_tv, ResetTool(), SaveTool()]
	plot_tv_tools_o = [HoverTool(tooltips=[("OHP", "@o_tv{1} : @ohp_total_vol{1}")], names=["o_tv"],mode='vline'), PanTool(dimensions='width'), wz_tv, ResetTool(), SaveTool()]

	data['date_str'] = data['date'].map(str)

	cds_max = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], stair_amount=data['stair_amount'], squat_max=data['squat_max'], deadlift_max=data['deadlift_max'], bench_max=data['bench_max'], ohp_max=data['ohp_max']))

	#MVPS and TV plots are hooked into the MA slider, so share a cds
	cds_w = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], stair_amount=data['stair_amount'], squat_max=data['squat_max'], deadlift_max=data['deadlift_max'], bench_max=data['bench_max'], ohp_max=data['ohp_max'], squat_max_vol_per_set=data['squat_max_vol_per_set'], deadlift_max_vol_per_set=data['deadlift_max_vol_per_set'], bench_max_vol_per_set=data['bench_max_vol_per_set'], ohp_max_vol_per_set=data['ohp_max_vol_per_set'], squat_total_vol=data['squat_total_vol'], deadlift_total_vol=data['deadlift_total_vol'], bench_total_vol=data['bench_total_vol'], ohp_total_vol=data['ohp_total_vol']))
	cds_s = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], stair_amount=data['stair_amount'], squat_max=data['squat_max'], deadlift_max=data['deadlift_max'], bench_max=data['bench_max'], ohp_max=data['ohp_max'], squat_max_vol_per_set=data['squat_max_vol_per_set'], deadlift_max_vol_per_set=data['deadlift_max_vol_per_set'], bench_max_vol_per_set=data['bench_max_vol_per_set'], ohp_max_vol_per_set=data['ohp_max_vol_per_set'], squat_total_vol=data['squat_total_vol'], deadlift_total_vol=data['deadlift_total_vol'], bench_total_vol=data['bench_total_vol'], ohp_total_vol=data['ohp_total_vol']))

	d = cds_max.data
	d_w = cds_w.data

	#Calculate clamp values
	s_m, d_m, b_m, o_m, s_mvps, d_mvps, b_mvps, o_mvps, s_tv, d_tv, b_tv, o_tv = [], [], [], [], [], [], [], [], [], [], [], []

	#***TODO: Make general
	#First values
	s_m.append(155.0)
	d_m.append(145.0)
	b_m.append(135.0)
	o_m.append(70.0)
	s_mvps.append(775.0)
	d_mvps.append(725.0)
	b_mvps.append(675.0)
	o_mvps.append(350.0)
	s_tv.append(4425.0)
	d_tv.append(2650.0)
	b_tv.append(3525.0)
	o_tv.append(1700.0)

	#Find max of all previous values to clamp
	for c in range(1,len(d['date'])):
		#Clamp
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

		#Extend
		if math.isnan(d_w['squat_max_vol_per_set'][c]):
			s_mvps.append(s_mvps[c - 1])
		else:
			s_mvps.append(d_w['squat_max_vol_per_set'][c])
		if math.isnan(d_w['deadlift_max_vol_per_set'][c]):
			d_mvps.append(d_mvps[c - 1])
		else:
			d_mvps.append(d_w['deadlift_max_vol_per_set'][c])
		if math.isnan(d_w['bench_max_vol_per_set'][c]):
			b_mvps.append(b_mvps[c - 1])
		else:
			b_mvps.append(d_w['bench_max_vol_per_set'][c])
		if math.isnan(d_w['ohp_max_vol_per_set'][c]):
			o_mvps.append(o_mvps[c - 1])
		else:
			o_mvps.append(d_w['ohp_max_vol_per_set'][c])

		if math.isnan(d_w['squat_total_vol'][c]):
			s_tv.append(s_tv[c - 1])
		else:
			s_tv.append(d_w['squat_total_vol'][c])
		if math.isnan(d_w['deadlift_total_vol'][c]):
			d_tv.append(d_tv[c - 1])
		else:
			d_tv.append(d_w['deadlift_total_vol'][c])
		if math.isnan(d_w['bench_total_vol'][c]):
			b_tv.append(b_tv[c - 1])
		else:
			b_tv.append(d_w['bench_total_vol'][c])
		if math.isnan(d_w['ohp_total_vol'][c]):
			o_tv.append(o_tv[c - 1])
		else:
			o_tv.append(d_w['ohp_total_vol'][c])

	cds_max.add(d['date'], name='date')
	cds_max.add(s_m, name='s_m')
	cds_max.add(d_m, name='d_m')
	cds_max.add(b_m, name='b_m')
	cds_max.add(o_m, name='o_m')

	cds_w.add(d['date'], name='date')
	cds_w.add(s_mvps, name='s_mvps')
	cds_w.add(d_mvps, name='d_mvps')
	cds_w.add(b_mvps, name='b_mvps')
	cds_w.add(o_mvps, name='o_mvps')

	cds_w.add(s_tv, name='s_tv')
	cds_w.add(d_tv, name='d_tv')
	cds_w.add(b_tv, name='b_tv')
	cds_w.add(o_tv, name='o_tv')

	cds_s.add(d['date'], name='date')
	cds_s.add(s_mvps, name='s_mvps')
	cds_s.add(d_mvps, name='d_mvps')
	cds_s.add(b_mvps, name='b_mvps')
	cds_s.add(o_mvps, name='o_mvps')

	cds_s.add(s_tv, name='s_tv')
	cds_s.add(d_tv, name='d_tv')
	cds_s.add(b_tv, name='b_tv')
	cds_s.add(o_tv, name='o_tv')

	plot_max = figure(x_axis_type="datetime", title="MAXes", h_symmetry=False, v_symmetry=False,
				  min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", active_scroll=wz_max,tools=plot_max_tools_d)
	
	plot_max.yaxis.axis_label = "lbs"

	#sr = plot_max.circle('date', 'squat_max', source=cds_max, size=10, fill_color="grey", hover_fill_color="firebrick", fill_alpha=0.00, hover_alpha=0.3, line_color=None, hover_line_color="white")
	#dr = plot_max.circle('date', 'deadlift_max', source=cds_max, size=10, fill_color="grey", hover_fill_color="firebrick", fill_alpha=0.00, hover_alpha=0.3, line_color=None, hover_line_color="white")
	#br = plot_max.circle('date', 'bench_max', source=cds_max, size=10, fill_color="grey", hover_fill_color="firebrick", fill_alpha=0.00, hover_alpha=0.3, line_color=None, hover_line_color="white")
	#ohpr = plot_max.circle('date', 'ohp_max', source=cds_max, size=10, fill_color="grey", hover_fill_color="firebrick", fill_alpha=0.00, hover_alpha=0.3, line_color=None, hover_line_color="white")

	#plot_max.add_tools(HoverTool(tooltips=None, renderers=[sr, dr, br, ohpr], mode='vline'))
	plot_max.add_tools(plot_max_tools_s[0], plot_max_tools_b[0] ,plot_max_tools_o[0])

	plot_max.line('date', 's_m', source=cds_max, name='squat_clamp', line_color="#8B0A50", line_width=2, line_alpha=0.6, legend="Squat (Clamp)")
	plot_max.cross('date', 'squat_max', source=cds_max, name="squat_max", line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat (Actual)")    

	plot_max.line('date', 'd_m', source=cds_max, name='deadlift_clamp', line_color="#333366", line_width=2, line_alpha=0.6, legend="Deadlift (Clamp)")
	plot_max.cross('date', 'deadlift_max', source=cds_max, name="deadlift_max", line_color="#333366", line_width=1, line_alpha=0.6, legend="Deadlift (Actual)")    

	plot_max.line('date', 'b_m', source=cds_max, name='bench_clamp', line_color="#FF7700", line_width=2, line_alpha=0.6, legend="Bench Press (Clamp)")
	plot_max.cross('date', 'bench_max', source=cds_max, name="bench_max", line_color="#FF7700", line_width=1, line_alpha=0.6, legend="Bench Press (Actual)")    

	plot_max.line('date', 'o_m', source=cds_max, name='ohp_clamp', line_color="#C74D56", line_width=2, line_alpha=0.6, legend="OHP (Clamp)")
	plot_max.cross('date', 'ohp_max', source=cds_max, name="ohp_max", line_color="#C74D56", line_width=1, line_alpha=0.6, legend="OHP (Actual)")    

	plot_max.legend.location = "top_left"
	plot_max.legend.click_policy="hide"

	#MVPS
	plot_mvps = figure(x_axis_type="datetime", title="Maximum Volume Per Set", h_symmetry=False, v_symmetry=False,
				  min_border=0, plot_height=height, plot_width=width, x_range=plot_max.x_range, toolbar_location="above", outline_line_color="#666666", tools=plot_mvps_tools_d, active_scroll=wz_mvps)

	plot_mvps.add_tools(plot_mvps_tools_s[0], plot_mvps_tools_b[0] ,plot_mvps_tools_o[0])

	plot_mvps.cross('date', 'squat_max_vol_per_set', source=cds_s, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat")
	plot_mvps.line('date', 's_mvps', name="s_mvps", source=cds_w, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat (MA)")

	plot_mvps.cross('date', 'deadlift_max_vol_per_set', source=cds_s, line_color="#333366", line_width=1, line_alpha=0.6, legend="Deadlift")
	plot_mvps.line('date', 'd_mvps', name="d_mvps", source=cds_w, line_color="#333366", line_width=1, line_alpha=0.6, legend="Deadlift (MA)")

	plot_mvps.cross('date', 'bench_max_vol_per_set', source=cds_s, line_color="#FF7700", line_width=1, line_alpha=0.6, legend="Bench Press")
	plot_mvps.line('date', 'b_mvps', name="b_mvps", source=cds_w, line_color="#FF7700", line_width=1, line_alpha=0.6, legend="Bench Press (MA)")

	plot_mvps.cross('date', 'ohp_max_vol_per_set', source=cds_s, line_color="#C74D56", line_width=1, line_alpha=0.6, legend="Overhead Press")
	plot_mvps.line('date', 'o_mvps', name="o_mvps", source=cds_w, line_color="#C74D56", line_width=1, line_alpha=0.6, legend="Overhead Press (MA)")
				
	#glyph = X(x='date', y='squat_max_vol_per_set', line_color="#8B0A50", line_width=1, line_alpha=0.6)
	#plot_mvps.add_glyph(cds_mvps, glyph)
	plot_mvps.yaxis.axis_label = "lbs"
	plot_mvps.legend.location = "top_left"
	plot_mvps.legend.click_policy="hide"

	plot_tv = figure(x_axis_type="datetime", title="Total Volume", h_symmetry=False, v_symmetry=False,
				  min_border=0, plot_height=height, plot_width=width, x_range=plot_max.x_range, toolbar_location="above", outline_line_color="#666666", tools=plot_tv_tools_d, active_scroll=wz_tv)
	
	plot_tv.add_tools(plot_tv_tools_s[0], plot_tv_tools_b[0] ,plot_tv_tools_o[0])
	
	plot_tv.cross('date', 'squat_total_vol', source=cds_w, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat")
	plot_tv.line('date', 's_tv', name='s_tv', source=cds_w, line_color="#8B0A50", line_width=1, line_alpha=0.6, legend="Squat (MA)")

	plot_tv.cross('date', 'deadlift_total_vol', source=cds_w, line_color="#333366", line_width=1, line_alpha=0.6, legend="Deadlift")
	plot_tv.line('date', 'd_tv', name='d_tv', source=cds_w, line_color="#333366", line_width=1, line_alpha=0.6, legend="Deadlift (MA)")

	plot_tv.cross('date', 'bench_total_vol', source=cds_w, line_color="#FF7700", line_width=1, line_alpha=0.6, legend="Bench Press")
	plot_tv.line('date', 'b_tv', name='b_tv', source=cds_w, line_color="#FF7700", line_width=1, line_alpha=0.6, legend="Bench Press (MA)")

	plot_tv.cross('date', 'ohp_total_vol', source=cds_w, line_color="#C74D56", line_width=1, line_alpha=0.6, legend="Overhead Press")
	plot_tv.line('date', 'o_tv', name='o_tv', source=cds_w, line_color="#C74D56", line_width=1, line_alpha=0.6, legend="Overhead Press (MA)")

	plot_tv.yaxis.axis_label = "lbs"
	plot_tv.legend.location = "top_left"
	plot_tv.legend.click_policy="hide"

	div_squat_max = Div()
	div_deadlift_max = Div()
	div_bench_max = Div()
	div_ohp_max = Div()

	div_squat_max_vol_per_set = Div()
	div_deadlift_max_vol_per_set = Div()
	div_bench_max_vol_per_set = Div()
	div_ohp_max_vol_per_set = Div()

	div_squat_total_vol = Div()
	div_deadlift_total_vol = Div()
	div_bench_total_vol = Div()
	div_ohp_total_vol = Div()

	num_stairs = sum([_ for _ in data['stair_amount'] if math.isnan(_)==False])
	num_esb = num_stairs/1860

	div_stairs = Div(text=str(int(num_stairs)) + " (" + str(int(num_esb)) + " Empire State Bldg)")
	#(sum(data['squat_total_vol']) + sum(data['deadlift_total_vol']) + sum(data['bench_total_vol']) + sum(data['ohp_total_vol']))
	num_ohp = (sum([_ for _ in data['squat_total_vol'] if math.isnan(_)==False]) + sum([_ for _ in data['deadlift_total_vol'] if math.isnan(_)==False]) + sum([_ for _ in data['bench_total_vol'] if math.isnan(_)==False]) + sum([_ for _ in data['ohp_total_vol'] if math.isnan(_)==False]))/8200000
	div_num_ohp = Div(text=str('{0:.2f}'.format(num_ohp)))
	div_workouts = Div(text=str(len(data['date'])))


	ma_cb = CustomJS(args=dict(w=cds_w, s=cds_s), code=MA_SLIDER_CODE)
	#plot_mvps.x_range.callback = CustomJS(args=dict(s=cds_s), code=LIFTS_STATS_CODE
	plot_max.x_range.callback = CustomJS(args=dict(d_s_m=div_squat_max, d_d_m=div_deadlift_max, d_b_m=div_bench_max, d_o_m=div_ohp_max, d_s_mvps=div_squat_max_vol_per_set, d_d_mvps=div_deadlift_max_vol_per_set, d_b_mvps=div_bench_max_vol_per_set, d_o_mvps=div_ohp_max_vol_per_set, d_s_tv=div_squat_total_vol, d_d_tv=div_deadlift_total_vol, d_b_tv=div_bench_total_vol, d_o_tv=div_ohp_total_vol, s=cds_s), code=LIFTS_STATS_CODE)

	ma_slider = Slider(start=1, end=30, value=1, step=1, title="Moving Average", callback=ma_cb)
	return components((div_stairs, div_num_ohp, div_workouts, div_squat_max, div_deadlift_max, div_bench_max, div_ohp_max, div_squat_max_vol_per_set, div_deadlift_max_vol_per_set, div_bench_max_vol_per_set, div_ohp_max_vol_per_set, div_squat_total_vol, div_deadlift_total_vol, div_bench_total_vol, div_ohp_total_vol, plot_max, plot_mvps, plot_tv, ma_slider))
