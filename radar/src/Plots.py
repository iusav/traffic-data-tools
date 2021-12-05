# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 14:54:53 2018

@author: ifv-alex.gellner
"""

import numpy as np
import pandas as pd

from Tracks import group
from bokeh.models import ColumnDataSource, WheelZoomTool, Slider, Dropdown
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.server.server import Server

from Statistics import filterOutliers
    
import time


class Plot:
    port = 5006

    def show(self, track, group, name):

        server = None
        
        def modify_doc(doc):
            most_common_length = group[group['count'] == group['count'].max()].iloc[0].length

            """minP = group[group['length'] < most_common_length]
            asd = minP[minP['count'] == minP['count'].min()]
            print(asd)"""
            plot = figure(plot_height=600, plot_width=1000, x_axis_label='length', y_axis_label='count', title=name)
            plot.line(x=group['length'] + 500 - most_common_length, y=group['count'])  # / most_common_length * 500, y=group['count'])
            plot.x_range.start = 0  # min(group['length'])
            plot.x_range.end = 2600  # max(group['length'])
            plot.y_range.start = min(group['count'])
            plot.y_range.end = max(group['count'])
            
            plot2 = figure(plot_height=300, plot_width=1000, x_axis_label='length', y_axis_label='category', x_range=plot.x_range)
            plot2.circle(x=track['length'], y=track['category'])
            plot2.y_range.start = 0.5
            plot2.y_range.end = 4.5
            plot2.toolbar.active_scroll = plot2.select_one(WheelZoomTool) 
            doc.add_root(column(plot, plot2))

        server = Server({'/': modify_doc}, port=Plot.port)
        Plot.port = Plot.port + 1;
        server.start()
        server.io_loop.add_callback(server.show, "/")
        server.io_loop.start()
