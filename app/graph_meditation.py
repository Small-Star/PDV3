
import pandas as pd
import datetime
import math

from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, Slider, PanTool, WheelZoomTool, BoxZoomTool, ResetTool, SaveTool, CustomJS
from bokeh.models.glyphs import Line, VBar
from bokeh.models.markers import X
from bokeh.plotting import figure
from bokeh.charts import Line, Bar
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Div

from helper_functions import *

def meditation_graph(data):
	'''Meditation graphs'''
	script, plot_daily_div, plot_cumu_div = meditation_figs(data)
	return script, plot_daily_div, plot_cumu_div


def meditation_figs(data, height = 500, width = 1700):
	#Timeseries Plot
	bz_daily = BoxZoomTool()
	wz_cumu = WheelZoomTool(dimensions='width')

	plot_daily_tools = [PanTool(dimensions='width'), bz_daily, ResetTool(), SaveTool()]
	plot_cumu_tools = [PanTool(dimensions='width'), wz_cumu, ResetTool(), SaveTool()]

	data['date_str'] = data['date'].map(str)

	cds_w = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], meditation_time=data['meditation_time']))
	cds_s = ColumnDataSource(dict(date=data['date'], date_str=data['date_str'], meditation_time=data['meditation_time']))

	d = cds_w.data
	d_s = cds_w.data

	#Calculate weeklong MA value, and cumulative value
	m_t_ma, m_t_c = [], []

	# #MA (inital values: 10;0;0;10;10;10;10)
	m_t_ma.append(10.0)
	m_t_ma.append(5.0)
	m_t_ma.append(3.33)
	m_t_ma.append(5.0)
	m_t_ma.append(6.0)
	m_t_ma.append(6.67)
	m_t_ma.append(7.14)

	for j in range(7,len(d['date'])):
		m_t_ma.append((d['meditation_time'][j] + d['meditation_time'][j-1] + d['meditation_time'][j-2] + d['meditation_time'][j-3] + d['meditation_time'][j-4] + d['meditation_time'][j-5] + d['meditation_time'][j-6])/7.0)

	# print(d['date'].count())
	# print(d.get(datetime.date(2018,12,30)))
	cds_w.add(m_t_ma, name='m_t_ma')

	#Cumu (inital value: 10)
	m_t_c.append(10.0)

	for k in range(1,d['date'].count()):
		m_t_c.append(d['meditation_time'][k] + m_t_c[-1])

	cds_w.add(m_t_c, name='m_t_c')

	#PLOT DAILY
	plot_daily = figure(x_axis_type="datetime", title="Daily Meditation", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, toolbar_location="above",outline_line_color="#666666", tools=plot_daily_tools)
	glyph = VBar(x="date", top="meditation_time", bottom=0, width=.8, fill_color="#41A2E8", line_color="#41A2E8")
	plot_daily.add_glyph(cds_w, glyph)
	plot_daily.line('date', 'm_t_ma', name='m_t_ma', source=cds_w, line_color="#8B0A50", line_width=3, line_alpha=0.6, legend="Moving Average (7 days)")

	plot_daily.legend.location = "top_left"
	plot_daily.legend.click_policy="hide"
	plot_daily.yaxis.axis_label = "Minutes"

	#plot_daily.Bar('date', 'meditation_time', source=cds_w, name='meditation_time')
	plot_cumu = figure(x_axis_type="datetime", title="Cumulative Meditation", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, toolbar_location="above",outline_line_color="#666666", active_scroll=wz_cumu, tools=plot_cumu_tools)

	glyph = VBar(x="date", top="m_t_c", bottom=0, width=.8, fill_color="#41A2E8", line_color="#41A2E8")
	plot_cumu.add_glyph(cds_w, glyph)
	plot_cumu.yaxis.visible = False


	#plot_daily = Histogram(cds_w, 'meditation_time', title="Daily Meditation", plot_height=height, plot_width=width, active_scroll=wz)

	#plot_cumu = Histogram(cds_w, 'meditation_time', title="Daily Meditation", plot_height=height, plot_width=width, active_scroll=wz)
	#plot_max = figure(x_axis_type="datetime", title="MAXes", h_symmetry=False, v_symmetry=False, min_border=0, plot_height=height, plot_width=width, toolbar_location="above", outline_line_color="#666666", active_scroll=wz_max,tools=plot_max_tools_d)
	
	script, (plot_daily_div, plot_cumu_div) = components((plot_daily, plot_cumu))


	return script, plot_daily_div, plot_cumu_div