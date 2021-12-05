# -*- coding: utf-8 -*-
"""
Created on Thu Nov 1 20:06:53 2018

@author: ifv-alex.gellner
"""
import numpy as np
from bokeh.models import DatetimeTickFormatter, WheelZoomTool
from bokeh.plotting import figure
from bokeh.core.properties import value


class Plot(object):

    def __init__(self, x_range=(np.datetime64(0, 's'), np.datetime64(1, 's')), y_range=(0, 100), tools='xpan,xwheel_zoom,xbox_zoom,xbox_select,save'):
        self.name = "plot"
        self.plot = figure(plot_height=500, plot_width=1000, x_range=x_range, y_range=y_range, tools=tools)
        self.plot.toolbar.logo = None
        self.plot.xaxis.axis_label_text_font_size = '16px'
        self.plot.xaxis.axis_label_standoff = 16
        self.plot.xaxis.formatter = DatetimeTickFormatter(days=["%d.%m.%Y %H:00"],
                                                     hours=["%d.%m.%Y %H:00"],
                                                     minutes=["%d.%m.%Y %H:%M"],
                                                     seconds=["%H:%M:%S"])
    
        self.plot.yaxis.axis_label_text_font_size = '16px'
        self.plot.yaxis.axis_label_standoff = 16
    
        self.plot.title.text_font = 'arial'
        self.plot.title.text_font_size = '20px'
        self.plot.title.align = 'center'
    
        self.plot.toolbar.active_scroll = self.plot.select_one(WheelZoomTool)

    def setTitle(self, title):
        self.plot.title.text = title
        
    def setXLabel(self, text):
        self.plot.xaxis.axis_label = text
        
    def setYLabel(self, text):
        self.plot.yaxis.axis_label = text
        
    def setLegendLabel(self, index, text):
        self.plot.legend[0].items[index].label = value(text)
        
    def setLegendLabels(self, labels):
        for label, item in zip(labels, self.plot.legend[0].items):
            item.label = value(label)

    def setXAxisRange(self, start, end):
        self.plot.x_range.start = start
        self.plot.x_range.end = end
        
    def setYAxisRange(self, start, end):
        self.plot.y_range.start = start
        self.plot.y_range.end = end
        
    def setXResetAxisRange(self, start, end):
        self.plot.x_range.reset_start = start
        self.plot.x_range.reset_end = end
        
    def setYResetAxisRange(self, start, end):
        self.plot.y_range.reset_start = start
        self.plot.y_range.reset_end = end
        
    def resetAxes(self):
        self.plot.x_range.start = self.plot.x_range.reset_start
        self.plot.x_range.end = self.plot.x_range.reset_end
        
        self.plot.y_range.start = self.plot.y_range.reset_start
        self.plot.y_range.end = self.plot.y_range.reset_end